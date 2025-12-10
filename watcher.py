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

import run_analysis as ra


def run_analysis(logfile: Path, output_dir: Path):
    print(f"[watcher] Running analysis for: {logfile}")
    try:
        # call the runner which imports from src.elc_ph directly
        ra.run(str(logfile), str(output_dir))
        print(f"[watcher] Analysis complete. Results in: {output_dir}\n")
    except Exception as e:
        print(f"[watcher] Analysis failed: {e}")


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


def main():
    parser = argparse.ArgumentParser(description='Watch a log file and auto-run analysis when it changes.')
    parser.add_argument('--log', '-l', default='data/sample_errors.log', help='Path to log file to watch')
    parser.add_argument('--output', '-o', default='output', help='Output directory for analysis results')
    parser.add_argument('--interval', '-i', type=float, default=2.0, help='Polling interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')

    args = parser.parse_args()

    logfile = Path(args.log)
    output_dir = Path(args.output)

    watch(logfile, output_dir, interval=args.interval, once=args.once)


if __name__ == '__main__':
    main()
