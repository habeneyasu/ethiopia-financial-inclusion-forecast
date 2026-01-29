# 🇪🇹 Ethiopia Financial Inclusion Forecast

> Machine learning models to forecast and analyze financial inclusion trends in Ethiopia

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd ethiopia-financial-inclusion-forecast
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## 📁 Structure

```
data/raw/          → Input datasets
data/processed/    → Cleaned data
notebooks/         → Analysis & exploration
src/               → Source code
dashboard/         → Interactive dashboard
tests/             → Test suite
models/            → Trained models
reports/figures/   → Visualizations
```

## 💻 Usage

```bash
# Run dashboard
python dashboard/app.py

# Run tests
pytest tests/ -v

# Start Jupyter
jupyter notebook
```

## 🛠️ Development

```bash
# Format code
black .

# Run tests with coverage
pytest tests/ --cov=src
```

## 📊 Data

Place your datasets in `data/raw/`:
- `ethiopia_fi_unified_data.csv`
- `reference_codes.csv`

## 🤝 Contributing

1. Fork → Create branch → Make changes
2. Run tests → Format code → Submit PR

---

**Built with** Python • Pandas • Scikit-learn • Jupyter
