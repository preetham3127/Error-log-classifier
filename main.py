"""
Error Log Classifier - Main Application
Groups similar error log lines, extracts signatures, and generates reports.
"""

import sys
import argparse
import json
import gc
from pathlib import Path
from datetime import datetime

# Import core modules
from src.log_processor import LogProcessor
from src.signature_extractor import SignatureExtractor
from src.clustering import ErrorClusterer
from src.report_generator import ReportGenerator
from src.export_handler import ExportHandler
from src.diff_analyzer import DiffAnalyzer


class ErrorLogClassifier:
    """Main application class for error log analysis."""
    
    def __init__(self, chunk_size=1000):
        """
        Initialize the classifier.
        
        Args:
            chunk_size (int): Lines to process before memory cleanup
        """
        self.chunk_size = chunk_size
        self.log_processor = LogProcessor(chunk_size=chunk_size)
        self.signature_extractor = SignatureExtractor()
        self.clusterer = ErrorClusterer()
        self.report_gen = ReportGenerator()
        self.export_handler = ExportHandler()
    
    def analyze_log_file(self, filepath, max_lines=None, include_filter=None, 
                        exclude_filter=None, keywords=None, time_bucket=None):
        """
        Analyze a single log file.
        
        Args:
            filepath (str): Path to log file
            max_lines (int): Max lines to read
            include_filter (str): Regex to include lines
            exclude_filter (str): Regex to exclude lines
            keywords (list): Keywords that must appear
            time_bucket (int): Minutes per time bucket
            
        Returns:
            dict: Analysis report
        """
        print(f"\n{'='*70}")
        print(f"Analyzing: {filepath}")
        print(f"{'='*70}")
        
        # Step 1: Read logs
        print("Step 1: Reading log file...")
        logs = self.log_processor.read_logs(filepath, max_lines=max_lines)
        
        # Step 2: Filter logs if needed
        if include_filter or exclude_filter or keywords:
            print("Step 2: Filtering logs...")
            logs = self.log_processor.filter_logs(
                logs,
                pattern=include_filter,
                exclude_pattern=exclude_filter,
                error_keywords=keywords
            )
        
        # Step 3: Extract signatures and cluster
        print("Step 3: Extracting signatures and clustering...")
        lines_with_signatures = [
            (line_num, line, self.signature_extractor.get_signature(line))
            for line_num, line, _ in logs
        ]
        
        # Force garbage collection periodically
        if len(lines_with_signatures) % self.chunk_size == 0:
            gc.collect()
        
        clusters = self.clusterer.cluster_by_signature(lines_with_signatures)
        
        # Step 4: Get statistics
        print("Step 4: Calculating statistics...")
        logs_for_stats = self.log_processor.read_logs(filepath, max_lines=max_lines)
        stats = self.log_processor.get_stats(logs_for_stats)
        
        # Step 5: Generate report
        print("Step 5: Generating report...")
        report = self.report_gen.generate_summary(clusters, stats=stats)
        
        # Display summary
        self._display_summary(report)
        
        return report, clusters
    
    def export_results(self, report, output_dir, base_name="error_analysis"):
        """
        Export analysis results to CSV, JSON, and HTML with fixed filenames.
        Each run overwrites the previous output to maintain only latest results.
        
        Args:
            report (dict): The report dictionary
            output_dir (str): Output directory
            base_name (str): Base name for output files
            
        Returns:
            dict: Paths to created files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Use fixed filenames instead of timestamps - this allows outputs to update
        exported_files = {}
        
        # Export CSV
        csv_path = output_path / f"{base_name}.csv"
        result = self.export_handler.export_csv(report, str(csv_path))
        if result:
            exported_files['csv'] = result
            print(f"✓ CSV exported to: {result}")
        
        # Export JSON
        json_path = output_path / f"{base_name}.json"
        result = self.export_handler.export_json(report, str(json_path))
        if result:
            exported_files['json'] = result
            print(f"✓ JSON exported to: {result}")
        
        # Export HTML
        html_path = output_path / f"{base_name}.html"
        result = self.export_handler.export_html(report, str(html_path))
        if result:
            exported_files['html'] = result
            print(f"✓ HTML exported to: {result}")
        
        return exported_files
    
    def compare_reports(self, baseline_path, current_path, output_dir):
        """
        Compare two analysis reports.
        
        Args:
            baseline_path (str): Path to baseline JSON report
            current_path (str): Path to current JSON report
            output_dir (str): Output directory
            
        Returns:
            dict: Diff analysis
        """
        print(f"\n{'='*70}")
        print("Comparing reports...")
        print(f"{'='*70}")
        
        # Load reports
        with open(baseline_path, 'r') as f:
            baseline = json.load(f)
        
        with open(current_path, 'r') as f:
            current = json.load(f)
        
        # Analyze diff
        analyzer = DiffAnalyzer()
        analyzer.load_baseline(baseline)
        analyzer.load_current(current)
        diff = analyzer.compare()
        
        # Display diff report
        print(analyzer.format_diff_report(diff))
        
        # Export diff
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        diff_path = output_path / f"diff_report_{timestamp}.json"
        analyzer.export_diff_json(diff, str(diff_path))
        print(f"\n✓ Diff report exported to: {diff_path}")
        
        return diff
    
    def _display_summary(self, report):
        """Display a summary of the report."""
        summary = report['summary']
        print("\n" + "-"*70)
        print("ANALYSIS SUMMARY")
        print("-"*70)
        print(f"Total Clusters:        {summary['total_clusters']}")
        print(f"Total Lines:           {summary['total_lines']:,}")
        print(f"Avg Cluster Size:      {summary['average_cluster_size']:.2f}")
        print(f"Largest Cluster:       {summary['largest_cluster']:,} occurrences")
        print(f"Smallest Cluster:      {summary['smallest_cluster']} occurrence")
        
        if report['top_clusters']:
            print("\n" + "-"*70)
            print("TOP 5 OFFENDERS")
            print("-"*70)
            for i, cluster in enumerate(report['top_clusters'][:5], 1):
                print(f"{i}. [{cluster['count']}] {cluster['signature'][:60]}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Error Log Classifier - Analyze and cluster error logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a log file
  python main.py analyze logs/error.log -o output
  
  # Filter by keyword
  python main.py analyze logs/error.log -o output -k "database" "connection"
  
  # Compare two runs
  python main.py diff baseline.json current.json -o output
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a log file')
    analyze_parser.add_argument('logfile', help='Path to log file')
    analyze_parser.add_argument('-o', '--output', required=True, help='Output directory')
    analyze_parser.add_argument('-m', '--max-lines', type=int, help='Maximum lines to read')
    analyze_parser.add_argument('-i', '--include', help='Regex pattern to include lines')
    analyze_parser.add_argument('-e', '--exclude', help='Regex pattern to exclude lines')
    analyze_parser.add_argument('-k', '--keywords', nargs='+', help='Keywords that must appear')
    analyze_parser.add_argument('-t', '--time-bucket', type=int, help='Time bucket in minutes')
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Compare two analysis runs')
    diff_parser.add_argument('baseline', help='Path to baseline JSON report')
    diff_parser.add_argument('current', help='Path to current JSON report')
    diff_parser.add_argument('-o', '--output', required=True, help='Output directory')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Display project information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'info':
        print("""
╔════════════════════════════════════════════════════════════════╗
║         ERROR LOG CLASSIFIER - Project Information             ║
╚════════════════════════════════════════════════════════════════╝

PURPOSE:
  Analyze large error logs and cluster lines by similarity to identify
  recurring failures and operational issues quickly.

FEATURES:
  • Text normalization and signature extraction
  • Similarity-based clustering of error patterns
  • Frequency analysis and ranking
  • Memory-bounded processing for large files
  • CSV and HTML report generation
  • Regression tracking via diff analysis

MEMORY EFFICIENCY:
  • Processes logs in chunks with garbage collection
  • Streaming file reading (not loading entire file)
  • Configurable chunk sizes for different systems
  
KEY MODULES:
  • log_processor.py     - File reading and log filtering
  • signature_extractor.py - Normalization and pattern extraction
  • clustering.py         - Error pattern clustering
  • report_generator.py   - Report generation and formatting
  • export_handler.py     - CSV and HTML export
  • diff_analyzer.py      - Comparing analysis runs

USAGE:
  
  Analyze a log file:
    python main.py analyze data/error.log -o output
  
  With filters:
    python main.py analyze data/error.log -o output \\
      -k "database" "timeout" \\
      -e "INFO|DEBUG"
  
  Compare two runs:
    python main.py diff output/analysis_run1.json \\
                        output/analysis_run2.json -o output

DATA FLOW:
  Log File → Read (streaming) → Filter → Extract Signatures → 
  Cluster → Analyze → Generate Reports → Export (CSV/JSON/HTML)
        """)
    
    elif args.command == 'analyze':
        classifier = ErrorLogClassifier()
        
        # Check if log file exists
        if not Path(args.logfile).exists():
            print(f"Error: Log file not found: {args.logfile}")
            sys.exit(1)
        
        try:
            report, clusters = classifier.analyze_log_file(
                args.logfile,
                max_lines=args.max_lines,
                include_filter=args.include,
                exclude_filter=args.exclude,
                keywords=args.keywords,
                time_bucket=args.time_bucket
            )
            
            # Export results
            print(f"\n{'='*70}")
            print("Exporting results...")
            print(f"{'='*70}")
            exported = classifier.export_results(
                report,
                args.output,
                base_name="error_analysis"
            )
            
            print(f"\n{'='*70}")
            print("✓ Analysis complete!")
            print(f"{'='*70}")
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif args.command == 'diff':
        classifier = ErrorLogClassifier()
        
        # Check if files exist
        if not Path(args.baseline).exists():
            print(f"Error: Baseline file not found: {args.baseline}")
            sys.exit(1)
        if not Path(args.current).exists():
            print(f"Error: Current file not found: {args.current}")
            sys.exit(1)
        
        try:
            classifier.compare_reports(
                args.baseline,
                args.current,
                args.output
            )
        except Exception as e:
            print(f"Error during comparison: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()

