# Error Log Classifier - Complete Project Index

**Group 106** - Preetham Ghorpade (251810700340) & Harish R S (251810700315)

## 📋 Project Overview

The Error Log Classifier is a production-ready Python tool that analyzes error logs at scale, identifies recurring patterns through intelligent clustering, and generates actionable reports in multiple formats (CSV, JSON, HTML).

**Key Achievement:** Tracks regressions between runs with diff analysis and maintains constant memory bounds regardless of log file size.

---

## 📁 Complete Project Structure

```
ELC-PH/
├── main.py                          # Entry point - CLI interface
├── README.md                        # Main project documentation
│
├── src/                             # Core application modules
│   ├── __init__.py                  # Package initialization
│   ├── log_processor.py             # File I/O, filtering, bucketing
│   ├── signature_extractor.py       # Normalization, pattern extraction
│   ├── clustering.py                # Error clustering algorithm
│   ├── report_generator.py          # Report generation
│   ├── export_handler.py            # CSV/JSON/HTML export
│   └── diff_analyzer.py             # Regression detection
│
├── data/                            # Sample data
│   └── sample_errors.log            # Dynamic test log (editable!)
│
├── output/                          # Generated reports (created at runtime)
│   ├── run1/                        # First analysis results
│   ├── run2/                        # Second analysis results
│   ├── comparison/                  # Diff analysis results
│   └── error_analysis_*.{csv,json,html}  # Individual reports
│
├── tests/                           # Unit tests
│   └── test_modules.py              # Test suite for all modules
│
└── docs/                            # Documentation
    ├── README.md                    # Quick overview
    ├── QUICKSTART.md                # 5-minute getting started
    ├── EXAMPLES.md                  # Real-world usage examples
    ├── DYNAMIC_TESTING.md           # How to modify sample log
    └── ARCHITECTURE.md              # System design & extensibility
```

---

## 🚀 Quick Start (2 Minutes)

```bash
# 1. Analyze sample errors
python main.py analyze data/sample_errors.log -o output

# 2. View results
start output/error_analysis_*.html

# 3. Done! Examine the HTML dashboard report
```

**What you get:**
- ✅ `error_analysis_*.csv` - Spreadsheet format
- ✅ `error_analysis_*.json` - Machine-readable
- ✅ `error_analysis_*.html` - Beautiful dashboard

---

## 📚 Documentation Files

### For Quick Learning
| File | Time | Best For |
|------|------|----------|
| `README.md` | 5 min | Overview and basic commands |
| `QUICKSTART.md` | 5 min | Getting started immediately |
| `DYNAMIC_TESTING.md` | 10 min | Understanding how tool works |

### For Advanced Usage
| File | Time | Best For |
|------|------|----------|
| `EXAMPLES.md` | 15 min | Real-world scenarios |
| `ARCHITECTURE.md` | 20 min | System design and extending |

---

## 💻 Core Modules
