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
- Event-indicator association matrix built with impact magnitudes and directions
- Three functional forms implemented for effect representation (immediate, gradual, distributed)
- Historical validation framework established for model refinement

## 🏗️ Project Architecture

```
Data Loading → Exploration → Enrichment → Analysis → Modeling → Forecasting → Dashboard
     ↓              ↓            ↓            ↓          ↓           ↓           ↓
 DataLoader   DataExplorer  DataEnricher    EDA      Impact     Forecasts   Streamlit
```

**Core Components:**
- **Data Layer**: Unified schema handling (observations, events, impact links)
- **Analysis Layer**: Exploratory data analysis and quality assessment
- **Modeling Layer**: Event impact estimation with association matrices and validation
- **Forecasting Layer**: Time series forecasting with scenario analysis (upcoming)
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
│   ├── 01_eda_analysis.ipynb
│   └── 02_event_impact_modeling.ipynb
├── src/
│   ├── utils/                 # Logger, config management
│   ├── data/                   # DataLoader, DataExplorer, DataEnricher
│   ├── analysis/               # EDA analyzer and visualizer
│   ├── models/                 # Event impact modeler, association matrix builder
│   ├── tasks/                  # Task executors
│   └── reports/                # Report generator
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

# Run Data Exploration & Enrichment
python -m src.tasks.task1_data_exploration

# Inspect data quality
python inspect_data_quality.py

# Run Exploratory Data Analysis
python -m src.tasks.task2_eda

# Run Event Impact Modeling
python -m src.tasks.task3_event_impact
```

## 🚀 Methodology & Features

### Data Exploration & Enrichment ✅

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

### Exploratory Data Analysis ✅

**Objective**: Analyze patterns and factors influencing financial inclusion in Ethiopia.

**Key Features:**
- Comprehensive dataset overview and quality assessment
- Temporal coverage matrix and gap identification
- Access trajectory analysis with growth rate calculations
- Usage trends and digital payment adoption patterns
- Infrastructure and enabler variable analysis
- Event timeline visualization with impact overlays
- Correlation analysis between indicators
- Gender gap analysis (if data available)
- Data gap identification and limitations assessment

**Usage:**
```bash
# Run EDA pipeline
python -m src.tasks.task2_eda

# Interactive analysis in Jupyter
jupyter notebook notebooks/01_eda_analysis.ipynb
```

```python
from src.analysis import EDAAnalyzer, DataVisualizer

# Initialize and analyze
eda = EDAAnalyzer()
visualizer = DataVisualizer(eda)

# Get insights
overview = eda.get_dataset_overview()
access_traj = eda.analyze_access_trajectory()
correlation = eda.analyze_correlations()
gaps = eda.identify_data_gaps()

# Visualize
visualizer.plot_access_trajectory(show_events=True)
visualizer.plot_correlation_heatmap()
```

### Event Impact Modeling ✅

**Objective**: Model how events (policies, product launches, infrastructure investments) affect financial inclusion indicators.

**Key Features:**
- Impact data loading and joining with events
- Event-indicator association matrix construction
- Three functional forms for effect representation (immediate, gradual, distributed)
- Multiple event effect combination methods (additive, multiplicative, max)
- Historical data validation against known impacts
- Comparable country evidence integration
- Impact estimation refinement based on validation
- Comprehensive methodology documentation

**Usage:**
```bash
# Run event impact modeling pipeline
python -m src.tasks.task3_event_impact

# Interactive analysis in Jupyter
jupyter notebook notebooks/02_event_impact_modeling.ipynb
```

```python
from src.models import EventImpactModeler, AssociationMatrixBuilder, ComparableEvidence

# Initialize modeler
impact_modeler = EventImpactModeler()
matrix_builder = AssociationMatrixBuilder(impact_modeler)

# Load impact data
impact_data = impact_modeler.load_impact_data()

# Build association matrix
association_matrix = matrix_builder.build_association_matrix()

# Visualize matrix
matrix_builder.visualize_matrix(association_matrix)

# Validate against historical data
validation_result = impact_modeler.validate_against_historical_data(
    indicator_code="ACC_MM_ACCOUNT",
    event_id="EVT_0001",
    observed_change=4.75,
    observed_period=("2021-05-01", "2024-12-31")
)

# Represent event effect over time
effect_series = impact_modeler.represent_event_effect_over_time(
    event_date=pd.Timestamp("2021-05-17"),
    impact_magnitude=5.0,
    lag_months=6,
    effect_type="gradual"
)

# Combine multiple event effects
combined = impact_modeler.combine_multiple_event_effects(
    [effect1, effect2],
    combination_method="additive"
)
```

**Key Deliverables:**
- Event-indicator association matrix (CSV + heatmap visualization)
- Impact summary showing which events affect which indicators
- Validation results comparing predicted vs. observed impacts
- Methodology documentation with assumptions and limitations
- Comparable country evidence database

### Forecasting Access and Usage ✅

**Objective**: Forecast Account Ownership (Access) and Digital Payment Usage for 2025-2027.

**Key Features:**
- Trend regression models (linear/log-linear)
- Event-augmented forecasts incorporating Task 3 impact modeling
- Scenario analysis (optimistic, base, pessimistic)
- Confidence intervals (95% prediction intervals)
- Uncertainty quantification and explicit limitation acknowledgment
- Comprehensive forecast tables and visualizations

**Usage:**
```bash
# Run forecasting pipeline
python -m src.tasks.task4_forecasting

# Interactive analysis in Jupyter
jupyter notebook notebooks/03_forecasting.ipynb
```

```python
from src.models import ForecastModeler

# Initialize forecaster
forecast_modeler = ForecastModeler()

# Forecast Account Ownership
access_forecast = forecast_modeler.forecast_indicator(
    indicator_code="ACC_OWNERSHIP",
    pillar="ACCESS",
    forecast_years=[2025, 2026, 2027],
    include_events=True,
    model_type="linear",
    confidence_level=0.95
)

# Generate forecast table
table = forecast_modeler.generate_forecast_table(access_forecast, scenario="base")

# Access scenarios
scenarios = access_forecast["scenarios"]  # optimistic, base, pessimistic
```

**Forecast Targets:**
1. **Account Ownership Rate (Access)**: % of adults with account at financial institution or mobile money
2. **Digital Payment Usage**: % of adults who made or received digital payment

**Approach:**
Given sparse data (5 Findex points over 13 years), the system employs:
- **Trend Regression**: Linear trend continuation based on historical data
- **Event-Augmented Model**: Baseline trend + event effects from Task 3
- **Scenario Analysis**: Optimistic (×1.2), base, pessimistic (×0.8) scenarios

**Key Deliverables:**
- Forecast tables with confidence intervals for 2025-2027
- Scenario comparison visualizations
- Written interpretation of predictions and uncertainties
- Methodology documentation
- Explicit acknowledgment of limitations

### Interactive Dashboard

**Objective**: Create interactive dashboard for stakeholder exploration.

**Key Deliverables:**
- Streamlit application
- Interactive visualizations
- Forecast displays with uncertainty bounds

## 📊 Reports & Dashboard

### Policy Report

Generate comprehensive policy-focused report for Tasks 1 & 2:

```bash
python generate_policy_report.py
```

**Report includes:**
- Executive summary with key highlights
- 4 data tables (Dataset composition, Pillar breakdown, Access trajectory, Events)
- 4 visualizations (Access trajectory, Usage trends, Event timeline, Correlation matrix)
- 5 policy recommendations
- Maximum 8 pages, designed for policy makers

Report saved to `reports/policy_report.md` with figures in `reports/figures/`.

### Interactive Dashboard

*Dashboard will be available after Interactive Dashboard development*

```bash
# Run dashboard
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
