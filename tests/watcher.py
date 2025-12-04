"""
watcher.py

Simple file-watcher that reruns the analysis whenever the sample log changes.
Uses a polling loop (no external dependencies) so it works on plain Python.

Usage:
  python watcher.py            # runs and watches indefinitely (poll every 2s)
  python watcher.py --once     # run analysis once and exit
  python watcher.py -i 5       # poll every 5 seconds

"""
import time
import argparse
from pathlib import Path

from main import ErrorLogClassifier


def run_analysis(logfile: Path, output_dir: Path):
    print(f"[watcher] Running analysis for: {logfile}")
    classifier = ErrorLogClassifier()
    report, clusters = classifier.analyze_log_file(str(logfile))
    classifier.export_results(report, str(output_dir))
    print(f"[watcher] Analysis complete. Results in: {output_dir}\n")


def watch(logfile: Path, output_dir: Path, interval: float = 2.0, once: bool = False):
    if not logfile.exists():
        raise SystemExit(f"Log file not found: {logfile}")
    
    last_mtime = logfile.stat().st_mtime

    # Run once immediately
    run_analysis(logfile, output_dir)

    if once:
        return

    print(f"[watcher] Watching '{logfile}' for changes (interval={interval}s). Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(interval)
            try:
                mtime = logfile.stat().st_mtime
            except FileNotFoundError:
                print(f"[watcher] Log file removed: {logfile}")
                continue

            if mtime != last_mtime:
                last_mtime = mtime
                print(f"[watcher] Change detected at {time.strftime('%Y-%m-%d %H:%M:%S')}, re-running analysis...")
                run_analysis(logfile, output_dir)

    except KeyboardInterrupt:
        print('\n[watcher] Stopped by user.')
