"""Run analysis using the internal elc_ph package (wrapper to avoid import issues).

This script mirrors the logic in `main.py` but imports directly from
`src.elc_ph` to avoid import path pitfalls.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.elc_ph.log_processor import LogProcessor
from src.elc_ph.signature_extractor import SignatureExtractor
from src.elc_ph.clustering import ErrorClusterer
from src.elc_ph.report_generator import ReportGenerator
from src.elc_ph.export_handler import ExportHandler


def run(logfile: str = 'data/sample_errors.log', output_dir: str = 'output'):
    lp = LogProcessor()
    se = SignatureExtractor()
    cl = ErrorClusterer()
    rg = ReportGenerator()
    eh = ExportHandler()

    print(f"Running analysis on: {logfile}")
    logs = lp.read_logs(logfile)

    # Build signatures
    lines_with_signatures = [(ln, line, se.get_signature(line)) for ln, line, _ in logs]

    clusters = cl.cluster_by_signature(lines_with_signatures)
    stats = lp.get_stats(lp.read_logs(logfile))
    # Make total_lines reflect the exact number of physical lines in the file
    try:
        with open(logfile, 'r', encoding='utf-8', errors='ignore') as f:
            stats['total_lines'] = sum(1 for _ in f)
    except Exception:
        pass

    report = rg.generate_summary(clusters, stats=stats)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    eh.export_csv(report, str(out / 'error_analysis.csv'))
    eh.export_json(report, str(out / 'error_analysis.json'))
    eh.export_html(report, str(out / 'error_analysis.html'))

    print('Analysis finished — outputs written to', out)


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('logfile', nargs='?', default='data/sample_errors.log')
    p.add_argument('-o', '--output', default='output')
    args = p.parse_args()
    run(args.logfile, args.output)
