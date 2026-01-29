# 🇪🇹 Forecasting Financial Inclusion in Ethiopia

> A data-driven forecasting system modeling Ethiopia's financial inclusion trajectory using time series methods and event impact analysis

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Table of Contents

- [Overview & Business Need](#-overview--business-need)
- [Key Insights & Forecast Highlights](#-key-insights--forecast-highlights)
- [Project Architecture](#️-project-architecture)
- [Repository Structure](#-repository-structure)
- [Installation & Quick Start](#-installation--quick-start)
- [Methodology & Task Overview](#-methodology--task-overview)
- [Dashboard](#-dashboard)
- [Development & Testing](#-development--testing)
- [References & License](#-references--license)

## 🎯 Overview & Business Need

You are a Data Scientist at Selam Analytics, a financial technology consulting firm specializing in emerging markets. Selam Analytics has been engaged by a consortium of stakeholders, including development finance institutions, mobile money operators, and the National Bank of Ethiopia, to develop a financial inclusion forecasting system.

Ethiopia is undergoing a rapid digital financial transformation. Telebirr has grown to over 54 million users since launching in 2021. M-Pesa entered the market in 2023 and now has over 10 million users. For the first time, interoperable P2P digital transfers have surpassed ATM cash withdrawals. Yet according to the 2024 Global Findex survey, only 49% of Ethiopian adults have a financial account; just 3 percentage points higher than in 2021.

The consortium wants to understand:

- What drives financial inclusion in Ethiopia?
- How do events like product launches, policy changes, and infrastructure investments affect inclusion outcomes?
- How did financial inclusion rates change in 2025 and how will it look like in the coming years - 2026 and 2027?

### The Global Findex Framework

The Global Findex Database is the world's most comprehensive demand-side survey of financial inclusion, conducted every three years since 2011.

**Access (Account Ownership)**: The share of adults (age 15+) who report having an account at a financial institution or using a mobile money service.

**Ethiopia's trajectory:**
- 2011: 14%
- 2014: 22% (+8pp)
- 2017: 35% (+13pp)
- 2021: 46% (+11pp)
- 2024: 49% (+3pp)

**Usage (Digital Payments)**: The share of adults who report using mobile money, cards, or digital channels to make payments.

## ✨ Key Insights & Forecast Highlights

*Forecasts and insights will be updated as tasks progress*

**Current Dataset Analysis:**
- 43 records: 30 observations, 10 events, 3 targets, 14 impact links
- Temporal coverage: 2014-2030
- 29 unique indicators across ACCESS, USAGE, GENDER, AFFORDABILITY pillars
- High confidence data: 40/43 records (93%)

**Key Findings:**
- Account ownership growth slowed to +3pp (2021-2024) despite 65M+ mobile money accounts
- 10 cataloged events including Telebirr launch (2021), M-Pesa entry (2023), policy changes
- 14 impact links modeling relationships between events and indicators

## 🏗️ Project Architecture

```
Data Loading → Exploration → Enrichment → Analysis → Modeling → Forecasting → Dashboard
     ↓              ↓            ↓            ↓          ↓           ↓           ↓
 DataLoader   DataExplorer  DataEnricher    EDA      Impact     Forecasts   Streamlit
```

**Core Components:**
- **Data Layer**: Unified schema handling (observations, events, impact links)
- **Analysis Layer**: Exploratory data analysis and quality assessment
- **Modeling Layer**: Event impact estimation and time series forecasting
- **Visualization Layer**: Interactive dashboard for stakeholder engagement

## 📁 Repository Structure

```
ethiopia-fi-forecast/
├── .github/workflows/
│   └── unittests.yml          # CI/CD pipeline
├── data/
│   ├── raw/                   # Starter dataset
│   │   ├── ethiopia_fi_unified_data.xlsx
│   │   ├── reference_codes.xlsx
│   │   └── Additional Data Points Guide.xlsx
│   └── processed/            # Analysis-ready data
├── notebooks/                 # Jupyter notebooks for analysis
├── src/
│   ├── utils/                 # Logger, config management
│   ├── data/                   # DataLoader, DataExplorer, DataEnricher
│   └── tasks/                  # Task executors
├── dashboard/
│   └── app.py                 # Interactive Streamlit dashboard
├── tests/                      # Unit tests
├── models/                     # Trained models
├── reports/
│   └── figures/               # Visualizations
├── requirements.txt
├── README.md
├── data_enrichment_log.md     # Enrichment tracking
└── .gitignore
```

## ⚙️ Installation & Quick Start

```bash
# Clone repository
git clone <repository-url>
cd ethiopia-financial-inclusion-forecast

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Task 1: Data Exploration
python -m src.tasks.task1_data_exploration

# Inspect data quality
python inspect_data_quality.py
```

## 🚀 Methodology & Task Overview

### Task 1: Data Exploration & Enrichment ✅

**Objective**: Understand the starter dataset and enrich it with additional data useful for forecasting.

**Key Deliverables:**
- Dataset exploration and quality assessment
- Enriched dataset with new observations, events, and impact links
- Comprehensive documentation in `data_enrichment_log.md`

**Usage:**
```python
from src.data import DataLoader, DataExplorer, DataEnricher

loader = DataLoader()
explorer = DataExplorer(loader)
enricher = DataEnricher(loader, explorer)

# Explore data
datasets = explorer.load_all_data()
counts = explorer.get_record_counts()
temporal = explorer.get_temporal_range()

# Add enrichments
enricher.add_observation(
    pillar="Access",
    indicator_code="ACC_OWNERSHIP",
    value_numeric=52.3,
    observation_date="2023-06-30",
    source_name="World Bank Findex",
    source_url="https://www.worldbank.org/globalfindex",
    confidence="high"
)
```

### Task 2: Exploratory Data Analysis

**Objective**: Analyze patterns and factors influencing financial inclusion in Ethiopia.

**Key Deliverables:**
- EDA notebook with visualizations
- Temporal coverage analysis
- Access and Usage trend analysis
- Event timeline visualization
- Correlation analysis

### Task 3: Event Impact Modeling

**Objective**: Model how events affect financial inclusion indicators.

**Key Deliverables:**
- Event-indicator association matrix
- Impact estimation methodology
- Validation against historical data

### Task 4: Forecasting Access and Usage

**Objective**: Forecast Account Ownership and Digital Payment Usage for 2025-2027.

**Key Deliverables:**
- Forecast models with confidence intervals
- Scenario analysis (optimistic, base, pessimistic)
- Written interpretation

### Task 5: Dashboard Development

**Objective**: Create interactive dashboard for stakeholder exploration.

**Key Deliverables:**
- Streamlit application
- Interactive visualizations
- Forecast displays with uncertainty bounds

## 📊 Dashboard

*Dashboard will be available after Task 5 completion*

```bash
# Run dashboard (after Task 5)
streamlit run dashboard/app.py
```

**Dashboard Features:**
- Overview page with key metrics
- Trends page with interactive time series
- Forecasts page with confidence intervals
- Inclusion projections with scenario selector

## 🔧 Development & Testing

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_data_loader.py -v
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 src

# Type checking
mypy src
```

### Data Quality Inspection

```bash
# Interactive inspection
python inspect_data_quality.py

# Generate exploration report
python -m src.tasks.task1_data_exploration
# Check: reports/task1_exploration_report.txt
```

### Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run tests: `pytest`
4. Format code: `black .`
5. Commit with descriptive messages
6. Submit pull request

## 📚 References & License

### Key References

- [Global Findex Database](https://www.worldbank.org/globalfindex) - World Bank's financial inclusion survey
- [National Bank of Ethiopia](https://www.nbe.gov.et) - Central bank reports and policies
- [EthSwitch S.C.](https://www.ethswitch.com) - Payment system operator
- [Ethio Telecom](https://www.ethiotelecom.et) - Mobile network operator

### Data Sources

- Global Findex Database (2011-2024)
- IMF Financial Access Survey
- GSMA State of the Industry Reports
- National Bank of Ethiopia reports
- Operator reports (Telebirr, M-Pesa, Safaricom)

### License

MIT License

---

**Built with** Python • Pandas • Scikit-learn • Streamlit • Plotly • Pytest
