# 🇪🇹 Forecasting Financial Inclusion in Ethiopia

> A data-driven forecasting system modeling Ethiopia's financial inclusion trajectory using time series methods and event impact analysis

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/yourusername/ethiopia-financial-inclusion-forecast/workflows/Unit%20Tests/badge.svg)](https://github.com/yourusername/ethiopia-financial-inclusion-forecast/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 Table of Contents

- [Project Overview & Impact](#-project-overview--impact)
- [Quick Start](#-quick-start)
- [Key Features](#-key-features)
- [Interactive Dashboard](#-interactive-dashboard)
- [Usage & Development](#-usage--development)
- [Project Status](#-project-status)

## 🎯 Project Overview & Impact

### The Challenge

Ethiopia is experiencing a **critical disconnect** between financial service supply and demand. Despite massive mobile money expansion:

- **65+ million mobile money accounts** registered since 2021
- **Only 49% of adults** report having a financial account (2024)
- **Growth slowed to +3pp** (2021-2024) vs. +11pp (2017-2021)

This **73% deceleration** reveals a fundamental gap: registered accounts ≠ active users. Policy makers need evidence-based insights to understand what drives financial inclusion and how to forecast future trends.

### The Solution

This project provides a **production-grade forecasting system** that:

- **Models event impacts**: Quantifies how policies, product launches, and infrastructure investments affect inclusion
- **Generates forecasts**: Projects account ownership and digital payment usage for 2025-2027 with confidence intervals
- **Enables scenario planning**: Optimistic, base, and pessimistic scenarios for policy decision-making
- **Visualizes insights**: Interactive dashboard for stakeholder exploration

### Real-World Impact

Developed for a consortium including:
- **National Bank of Ethiopia** (Central bank)
- **Development Finance Institutions**
- **Mobile Money Operators** (Telebirr, M-Pesa, Safaricom)

**Key Questions Answered:**
- What factors drive financial inclusion in Ethiopia?
- How do events (product launches, policy changes) affect outcomes?
- What will financial inclusion look like in 2025-2027?
- How can policy interventions be optimized?

## 🚀 Quick Start

Get up and running in under 2 minutes:

```bash
# 1. Clone and setup
git clone https://github.com/habeneyasu/ethiopia-financial-inclusion-forecast
cd ethiopia-financial-inclusion-forecast
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Launch the interactive dashboard (main output)
streamlit run dashboard/app.py
```

> **Note**: Replace `yourusername` with your GitHub username, or use your repository URL.

The dashboard will open at `http://localhost:8501` with:
- 📊 **Overview**: Key metrics and growth highlights
- 📈 **Trends**: Interactive time series analysis
- 🔮 **Forecasts**: 2025-2027 projections with confidence intervals
- 🎯 **Projections**: Progress toward 60% inclusion target

### Run Full Analysis Pipeline

```bash
# Data exploration and enrichment
python -m src.tasks.task1_data_exploration

# Exploratory data analysis
python -m src.tasks.task2_eda

# Event impact modeling
python -m src.tasks.task3_event_impact

# Generate forecasts
python -m src.tasks.task4_forecasting

# Generate policy report
python generate_policy_report.py
```

## ✨ Key Features

### 📈 Actionable Policy Insights
Translate complex data into clear forecasts and scenario visualizations for decision-makers. Generate policy-focused reports with visualizations, tables, and recommendations that answer "what will happen" and "what should we do."

### 🔍 Quantified Event Impact
Isolate and measure the effect of specific policies, product launches, or infrastructure investments on inclusion metrics. Build event-indicator association matrices that show which events drive which outcomes, with validated impact magnitudes.

### 🎯 Interactive Exploration
A self-service dashboard allows partners to explore data and answer their own questions. Interactive visualizations with filters, scenario selectors, and data export enable stakeholders to dive deep without technical expertise.

### 🔮 Evidence-Based Forecasting
Generate reliable forecasts for 2025-2027 with confidence intervals and scenario analysis. Combine trend analysis with event impact modeling to project future financial inclusion rates under different conditions.

### 📊 Comprehensive Analysis Pipeline
End-to-end workflow from data exploration through forecasting, with automated quality checks, enrichment capabilities, and reproducible analysis notebooks.

## 📊 Interactive Dashboard

**The dashboard is the project's main output** - an interactive tool for stakeholders to explore data, understand event impacts, and view forecasts.

![Dashboard Overview](docs/dashboard-screenshot.png)
*Interactive dashboard showing key metrics, trends, forecasts, and projections*

> **Note**: Add a screenshot or GIF of your dashboard here. Capture the Overview page showing key metrics and visualizations.

### Launch Dashboard

```bash
streamlit run dashboard/app.py
```

### Dashboard Pages

1. **📊 Overview**
   - Key metrics: Account ownership, total records, events, P2P/ATM ratio
   - Growth rate highlights with visualizations
   - Historical trajectory with event overlays
   - Data summary tables

2. **📈 Trends**
   - Interactive time series plots (2011-2024)
   - Date range selector
   - Multi-indicator comparison
   - Channel comparison (Access vs Usage)
   - CSV download

3. **🔮 Forecasts**
   - Account Ownership forecast (2025-2027)
   - Digital Payment Usage forecast
   - Model selection (linear/log)
   - Event effects toggle
   - Confidence level adjustment (80%-99%)
   - Scenario visualization
   - CSV download

4. **🎯 Inclusion Projections**
   - Financial inclusion projections (2025-2030)
   - Progress toward 60% target
   - Scenario selector (optimistic/base/pessimistic)
   - Target rate adjustment (50%-70%)
   - Scenario comparison tables
   - CSV download

**Technical Requirements Met:**
- ✅ At least 4 interactive visualizations
- ✅ Clear labels and explanations
- ✅ Data download functionality (CSV export)
- ✅ Interactive controls (filters, selectors, toggles)
- ✅ Responsive layout with sidebar navigation

## 📁 Project Structure

```
ethiopia-fi-forecast/
├── dashboard/
│   └── app.py                 # Interactive Streamlit dashboard (main output)
├── notebooks/                 # Jupyter notebooks for analysis
│   ├── 01_eda_analysis.ipynb
│   ├── 02_event_impact_modeling.ipynb
│   └── 03_forecasting.ipynb
├── src/
│   ├── data/                  # DataLoader, DataExplorer, DataEnricher
│   ├── analysis/               # EDA analyzer and visualizer
│   ├── models/                 # Event impact modeler, forecaster
│   ├── tasks/                  # Task executors
│   ├── reports/                # Report generator
│   └── utils/                  # Logger, config management
├── tests/                      # Unit tests
├── reports/                    # Generated reports and visualizations
├── data/
│   ├── raw/                   # Starter dataset
│   └── processed/             # Analysis-ready data
└── requirements.txt
```

*For detailed structure, see [Project Documentation](docs/STRUCTURE.md)*

## ⚙️ Installation

### Requirements

- **Python 3.9+** (tested on 3.9, 3.10, 3.11, 3.12)
- **pip** package manager

### Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Core Dependencies

- `pandas>=1.5.0` - Data manipulation
- `numpy>=1.23.0` - Numerical computing
- `scikit-learn>=1.2.0` - Machine learning
- `scipy>=1.10.0` - Statistical functions
- `plotly>=5.14.0` - Interactive visualizations
- `streamlit>=1.28.0` - Dashboard framework
- `openpyxl>=3.1.0` - Excel file support

*See [requirements.txt](requirements.txt) for complete list*

## 💻 Usage & Development

### Usage Examples

```python
# Data exploration
from src.data import DataLoader, DataExplorer
loader = DataLoader()
explorer = DataExplorer(loader)
datasets = explorer.load_all_data()

# Exploratory analysis
from src.analysis import EDAAnalyzer, DataVisualizer
eda = EDAAnalyzer()
visualizer = DataVisualizer(eda)
access_traj = eda.analyze_access_trajectory()
visualizer.plot_access_trajectory(show_events=True)

# Event impact modeling
from src.models import EventImpactModeler, AssociationMatrixBuilder
impact_modeler = EventImpactModeler()
matrix_builder = AssociationMatrixBuilder(impact_modeler)
association_matrix = matrix_builder.build_association_matrix()

# Forecasting
from src.models import ForecastModeler
forecast_modeler = ForecastModeler()
forecast = forecast_modeler.forecast_indicator(
    indicator_code="ACC_OWNERSHIP",
    pillar="ACCESS",
    forecast_years=[2025, 2026, 2027],
    include_events=True
)
```

### Development

**Testing:**
```bash
pytest                    # Run all tests
pytest --cov=src         # With coverage
```

**Code Quality:**
```bash
black .                  # Format code
flake8 src               # Lint
mypy src                 # Type checking
```

**Contributing:**
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Quick steps:
1. Fork and create feature branch
2. Make changes with tests
3. Run `pytest` and `black .`
4. Submit pull request

## 📝 Project Status

### ✅ Completed Features

- **Task 1**: Data Exploration & Enrichment
- **Task 2**: Exploratory Data Analysis
- **Task 3**: Event Impact Modeling
- **Task 4**: Forecasting Access and Usage
- **Task 5**: Interactive Dashboard Development

**All core features implemented and tested.**

### 🔮 Future Enhancements

- Additional forecasting models (ARIMA, Prophet)
- Real-time data integration
- Advanced scenario modeling
- Multi-country comparison framework
- API endpoints for programmatic access

### 📊 Current Capabilities

- **43 records** analyzed across 29 indicators
- **10 major events** cataloged and modeled
- **14 impact links** quantifying event-indicator relationships
- **Forecasts** for 2025-2027 with confidence intervals
- **Interactive dashboard** with 4 comprehensive pages

### 📚 References

- [Global Findex Database](https://www.worldbank.org/globalfindex) - World Bank's financial inclusion survey
- [National Bank of Ethiopia](https://www.nbe.gov.et) - Central bank reports
- Data sources: Global Findex (2011-2024), IMF, GSMA, NBE reports, operator data

### License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

*   **Developed by:** Haben Eyasu
*   This project was completed as part of the **10 Academy / Kifiya AI Master Program**. We thank the program instructors and mentors for their guidance.

---

**Built with** Python • Pandas • NumPy • Scikit-learn • Streamlit • Plotly • Pytest • OpenPyXL • SciPy

**Project Status**: ✅ Feature Complete | **Version**: 1.0.0 | **Last Updated**: January 2026
