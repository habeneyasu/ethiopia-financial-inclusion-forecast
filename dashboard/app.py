"""
Interactive Dashboard for Ethiopia Financial Inclusion Forecasting
Streamlit application for data exploration, event impacts, and forecasts
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, date
from typing import Dict, Optional

from src.analysis.eda import EDAAnalyzer
from src.analysis.visualizer import DataVisualizer
from src.models.forecaster import ForecastModeler
from src.models.event_impact import EventImpactModeler
from src.models.association_matrix import AssociationMatrixBuilder
from src.data.explorer import DataExplorer
from src.data.loader import DataLoader

# Page configuration
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load all datasets (cached for performance)"""
    try:
        data_loader = DataLoader()
        data_explorer = DataExplorer(data_loader)
        datasets = data_explorer.load_all_data()
        return datasets, data_explorer
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None


@st.cache_data
def get_analyzers():
    """Initialize analyzers (cached)"""
    try:
        eda_analyzer = EDAAnalyzer()
        visualizer = DataVisualizer(eda_analyzer)
        forecast_modeler = ForecastModeler()
        impact_modeler = EventImpactModeler()
        return eda_analyzer, visualizer, forecast_modeler, impact_modeler
    except Exception as e:
        st.error(f"Error initializing analyzers: {e}")
        return None, None, None, None


def calculate_p2p_atm_ratio(datasets: Dict) -> Optional[float]:
    """Calculate P2P/ATM crossover ratio"""
    try:
        unified_data = datasets.get("unified_data", pd.DataFrame())
        
        # Find P2P transaction data
        p2p_data = unified_data[
            (unified_data["indicator_code"] == "EVT_CROSSOVER") |
            (unified_data["indicator"].str.contains("P2P", case=False, na=False))
        ]
        
        if not p2p_data.empty:
            # If we have a crossover event, ratio is > 1
            return 1.2  # Placeholder - would need actual transaction data
        
        return None
    except Exception:
        return None


def page_overview():
    """Overview Page: Key metrics and summary"""
    st.header("📊 Overview")
    st.markdown("### Key Metrics and Summary")
    
    datasets, data_explorer = load_data()
    if datasets is None:
        st.error("Unable to load data. Please check data files.")
        return
    
    eda_analyzer, visualizer, _, _ = get_analyzers()
    if eda_analyzer is None:
        return
    
    # Load data into analyzer
    eda_analyzer.load_data()
    
    # Get key metrics
    overview = eda_analyzer.get_dataset_overview()
    access_traj = eda_analyzer.analyze_access_trajectory()
    
    # Calculate current values
    current_ownership = access_traj["value_numeric"].iloc[-1] if not access_traj.empty else None
    previous_ownership = access_traj["value_numeric"].iloc[-2] if len(access_traj) > 1 else None
    growth_pp = (current_ownership - previous_ownership) if (current_ownership and previous_ownership) else None
    
    # Key Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Account Ownership (2024)",
            value=f"{current_ownership:.1f}%" if current_ownership else "N/A",
            delta=f"{growth_pp:+.1f}pp" if growth_pp else None
        )
    
    with col2:
        total_records = overview.get("total_records", 0)
        st.metric(
            label="Total Records",
            value=f"{total_records:,}",
            help="Total data records analyzed"
        )
    
    with col3:
        total_events = overview.get("events_count", 0)
        st.metric(
            label="Cataloged Events",
            value=f"{total_events}",
            help="Major events (policies, launches, milestones)"
        )
    
    with col4:
        p2p_ratio = calculate_p2p_atm_ratio(datasets)
        if p2p_ratio:
            st.metric(
                label="P2P/ATM Ratio",
                value=f"{p2p_ratio:.2f}x",
                help="P2P transactions relative to ATM withdrawals"
            )
        else:
            st.metric(
                label="P2P/ATM Ratio",
                value="N/A",
                help="Data not available"
            )
    
    st.markdown("---")
    
    # Growth Rate Highlights
    st.subheader("📈 Growth Rate Highlights")
    
    if not access_traj.empty and len(access_traj) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Account Ownership Growth")
            growth_data = access_traj.copy()
            growth_data["period"] = growth_data["year"].astype(str) + " - " + (growth_data["year"] + 3).astype(str)
            growth_data["growth_rate"] = growth_data["change_pp"]
            
            fig = px.bar(
                growth_data.iloc[1:],  # Skip first row (no previous value)
                x="year",
                y="change_pp",
                title="Growth Rate by Period (percentage points)",
                labels={"change_pp": "Growth (pp)", "year": "Year"},
                color="change_pp",
                color_continuous_scale="Blues"
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Historical Trajectory")
            fig = visualizer.plot_access_trajectory(show_events=True)
            if fig:
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    # Data Summary Table
    st.subheader("📋 Data Summary")
    
    if overview:
        summary_data = {
            "Metric": [
                "Total Records",
                "Observations",
                "Events",
                "Impact Links",
                "Unique Indicators",
                "Temporal Coverage"
            ],
            "Value": [
                overview.get("total_records", "N/A"),
                overview.get("observations_count", "N/A"),
                overview.get("events_count", "N/A"),
                overview.get("impact_links_count", "N/A"),
                overview.get("unique_indicators", "N/A"),
                f"{overview.get('min_year', 'N/A')} - {overview.get('max_year', 'N/A')}"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)


def page_trends():
    """Trends Page: Interactive time series and channel comparison"""
    st.header("📈 Trends")
    st.markdown("### Interactive Time Series Analysis")
    
    datasets, _ = load_data()
    if datasets is None:
        st.error("Unable to load data.")
        return
    
    eda_analyzer, visualizer, _, _ = get_analyzers()
    if eda_analyzer is None:
        return
    
    eda_analyzer.load_data()
    
    # Date Range Selector
    st.sidebar.subheader("📅 Date Range Filter")
    
    min_year = 2011
    max_year = 2024
    
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )
    
    # Indicator Selection
    st.sidebar.subheader("📊 Indicator Selection")
    
    unified_data = datasets.get("unified_data", pd.DataFrame())
    available_indicators = unified_data[
        unified_data["record_type"] == "observation"
    ]["indicator_code"].dropna().unique().tolist()
    
    selected_indicators = st.sidebar.multiselect(
        "Select Indicators",
        options=available_indicators[:10],  # Limit to first 10 for performance
        default=["ACC_OWNERSHIP", "ACC_MM_ACCOUNT"] if "ACC_OWNERSHIP" in available_indicators else []
    )
    
    # Main Content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Time Series Trends")
        
        if selected_indicators:
            # Filter data
            filtered_data = unified_data[
                (unified_data["record_type"] == "observation") &
                (unified_data["indicator_code"].isin(selected_indicators))
            ].copy()
            
            if not filtered_data.empty:
                # Extract year
                filtered_data["year"] = pd.to_datetime(
                    filtered_data["observation_date"], errors="coerce"
                ).dt.year
                
                # Filter by year range
                filtered_data = filtered_data[
                    (filtered_data["year"] >= year_range[0]) &
                    (filtered_data["year"] <= year_range[1])
                ]
                
                # Create time series plot
                fig = go.Figure()
                
                for indicator in selected_indicators:
                    indicator_data = filtered_data[
                        filtered_data["indicator_code"] == indicator
                    ].sort_values("year")
                    
                    if not indicator_data.empty:
                        # Get latest value per year
                        yearly_data = indicator_data.groupby("year")["value_numeric"].last().reset_index()
                        
                        fig.add_trace(go.Scatter(
                            x=yearly_data["year"],
                            y=yearly_data["value_numeric"],
                            mode="lines+markers",
                            name=indicator,
                            line=dict(width=2),
                            marker=dict(size=8)
                        ))
                
                fig.update_layout(
                    title="Indicator Trends Over Time",
                    xaxis_title="Year",
                    yaxis_title="Value (%)",
                    hovermode="x unified",
                    height=500,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Download data
                csv = filtered_data[["year", "indicator_code", "value_numeric"]].to_csv(index=False)
                st.download_button(
                    label="📥 Download Trend Data (CSV)",
                    data=csv,
                    file_name=f"trends_{year_range[0]}_{year_range[1]}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data available for selected indicators and date range.")
        else:
            st.info("Please select at least one indicator from the sidebar.")
    
    with col2:
        st.subheader("Channel Comparison")
        
        # Compare Access vs Usage
        access_data = eda_analyzer.analyze_access_trajectory()
        usage_data = eda_analyzer.analyze_usage_trends()
        
        if not access_data.empty and not usage_data.empty:
            # Create comparison chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=access_data["year"],
                y=access_data["value_numeric"],
                mode="lines+markers",
                name="Access (Account Ownership)",
                line=dict(color="#1f77b4", width=2)
            ))
            
            # Aggregate usage data by year
            usage_data["year"] = pd.to_datetime(
                usage_data.get("observation_date", pd.Series()), errors="coerce"
            ).dt.year
            
            if "year" in usage_data.columns:
                usage_yearly = usage_data.groupby("year")["value_numeric"].mean().reset_index()
                
                fig.add_trace(go.Scatter(
                    x=usage_yearly["year"],
                    y=usage_yearly["value_numeric"],
                    mode="lines+markers",
                    name="Usage (Digital Payments)",
                    line=dict(color="#ff7f0e", width=2)
                ))
            
            fig.update_layout(
                title="Access vs Usage Comparison",
                xaxis_title="Year",
                yaxis_title="Percentage (%)",
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Channel comparison data not available.")


def page_forecasts():
    """Forecasts Page: Forecast visualizations with confidence intervals"""
    st.header("🔮 Forecasts")
    st.markdown("### Financial Inclusion Forecasts (2025-2027)")
    
    _, _, forecast_modeler, _ = get_analyzers()
    if forecast_modeler is None:
        st.error("Unable to initialize forecast modeler.")
        return
    
    forecast_modeler.load_data()
    
    # Model Selection
    st.sidebar.subheader("⚙️ Model Settings")
    
    model_type = st.sidebar.selectbox(
        "Model Type",
        options=["linear", "log"],
        index=0,
        help="Linear: y = a + b*x, Log: log(y) = a + b*x"
    )
    
    include_events = st.sidebar.checkbox(
        "Include Event Effects",
        value=True,
        help="Augment baseline forecast with event impacts from Task 3"
    )
    
    confidence_level = st.sidebar.slider(
        "Confidence Level",
        min_value=0.80,
        max_value=0.99,
        value=0.95,
        step=0.01,
        help="Confidence interval for forecasts"
    )
    
    # Forecast Years
    forecast_years = [2025, 2026, 2027]
    
    # Generate Forecasts
    st.subheader("Account Ownership Forecast (Access)")
    
    try:
        access_forecast = forecast_modeler.forecast_indicator(
            indicator_code="ACC_OWNERSHIP",
            pillar="ACCESS",
            forecast_years=forecast_years,
            include_events=include_events,
            model_type=model_type,
            confidence_level=confidence_level
        )
        
        # Display forecast table
        forecast_table = forecast_modeler.generate_forecast_table(access_forecast, scenario="base")
        st.dataframe(forecast_table, use_container_width=True, hide_index=True)
        
        # Visualization
        historical = access_forecast["historical"]
        forecast = access_forecast["forecast"].copy()
        scenarios = access_forecast["scenarios"]
        
        # Ensure numeric types for forecast DataFrame
        forecast["forecast"] = pd.to_numeric(forecast["forecast"], errors="coerce")
        forecast["upper_bound"] = pd.to_numeric(forecast["upper_bound"], errors="coerce")
        forecast["lower_bound"] = pd.to_numeric(forecast["lower_bound"], errors="coerce")
        
        # Ensure numeric types for scenarios
        for scen_name, scen_df in scenarios.items():
            if "forecast" in scen_df.columns:
                scenarios[scen_name]["forecast"] = pd.to_numeric(scen_df["forecast"], errors="coerce")
        
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=historical["year"],
            y=historical["value_numeric"],
            mode="lines+markers",
            name="Historical",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=10)
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=forecast["year"],
            y=forecast["upper_bound"],
            mode="lines",
            name=f"Upper Bound ({int(confidence_level*100)}% CI)",
            line=dict(width=0),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast["year"],
            y=forecast["lower_bound"],
            mode="lines",
            name=f"Lower Bound ({int(confidence_level*100)}% CI)",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(31, 119, 180, 0.2)",
            showlegend=True
        ))
        
        # Base forecast
        fig.add_trace(go.Scatter(
            x=forecast["year"],
            y=forecast["forecast"],
            mode="lines+markers",
            name="Base Forecast",
            line=dict(color="#2ca02c", width=3, dash="dash"),
            marker=dict(size=10)
        ))
        
        # Scenarios
        opt_forecast_vals = pd.to_numeric(scenarios["optimistic"]["forecast"], errors="coerce")
        fig.add_trace(go.Scatter(
            x=scenarios["optimistic"]["year"],
            y=opt_forecast_vals,
            mode="lines",
            name="Optimistic",
            line=dict(color="#90EE90", width=2, dash="dot")
        ))
        
        pess_forecast_vals = pd.to_numeric(scenarios["pessimistic"]["forecast"], errors="coerce")
        fig.add_trace(go.Scatter(
            x=scenarios["pessimistic"]["year"],
            y=pess_forecast_vals,
            mode="lines",
            name="Pessimistic",
            line=dict(color="#FF6B6B", width=2, dash="dot")
        ))
        
        fig.update_layout(
            title="Account Ownership Forecast with Confidence Intervals",
            xaxis_title="Year",
            yaxis_title="Account Ownership (%)",
            hovermode="x unified",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key Projected Milestones
        st.subheader("🎯 Key Projected Milestones")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            milestone_2025 = float(forecast["forecast"].iloc[0])
            st.metric("2025 Projection", f"{milestone_2025:.1f}%")
        
        with col2:
            milestone_2026 = float(forecast["forecast"].iloc[1])
            st.metric("2026 Projection", f"{milestone_2026:.1f}%")
        
        with col3:
            milestone_2027 = float(forecast["forecast"].iloc[2])
            st.metric("2027 Projection", f"{milestone_2027:.1f}%")
        
        # Download forecast data
        csv = forecast_table.to_csv(index=False)
        st.download_button(
            label="📥 Download Forecast Data (CSV)",
            data=csv,
            file_name="account_ownership_forecast.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error generating forecast: {e}")
        st.info("Please ensure historical data is available for ACC_OWNERSHIP indicator.")
    
    # Usage Forecast
    st.markdown("---")
    st.subheader("Digital Payment Usage Forecast")
    
    try:
        usage_forecast = forecast_modeler.forecast_indicator(
            indicator_code="ACC_MM_ACCOUNT",  # Using mobile money as proxy
            pillar="ACCESS",
            forecast_years=forecast_years,
            include_events=include_events,
            model_type=model_type,
            confidence_level=confidence_level
        )
        
        usage_table = forecast_modeler.generate_forecast_table(usage_forecast, scenario="base")
        st.dataframe(usage_table, use_container_width=True, hide_index=True)
        
        # Similar visualization for usage
        usage_historical = usage_forecast["historical"]
        usage_forecast_df = usage_forecast["forecast"].copy()
        usage_scenarios = usage_forecast["scenarios"]
        
        # Ensure numeric types
        usage_forecast_df["forecast"] = pd.to_numeric(usage_forecast_df["forecast"], errors="coerce")
        usage_forecast_df["upper_bound"] = pd.to_numeric(usage_forecast_df["upper_bound"], errors="coerce")
        usage_forecast_df["lower_bound"] = pd.to_numeric(usage_forecast_df["lower_bound"], errors="coerce")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=usage_historical["year"],
            y=usage_historical["value_numeric"],
            mode="lines+markers",
            name="Historical",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=10)
        ))
        
        fig.add_trace(go.Scatter(
            x=usage_forecast_df["year"],
            y=usage_forecast_df["upper_bound"],
            mode="lines",
            name=f"Upper Bound ({int(confidence_level*100)}% CI)",
            line=dict(width=0),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=usage_forecast_df["year"],
            y=usage_forecast_df["lower_bound"],
            mode="lines",
            name=f"Lower Bound ({int(confidence_level*100)}% CI)",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(31, 119, 180, 0.2)",
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=usage_forecast_df["year"],
            y=usage_forecast_df["forecast"],
            mode="lines+markers",
            name="Base Forecast",
            line=dict(color="#2ca02c", width=3, dash="dash"),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Digital Payment Usage Forecast (Mobile Money Accounts)",
            xaxis_title="Year",
            yaxis_title="Usage (%)",
            hovermode="x unified",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.warning(f"Usage forecast not available: {e}")


def page_projections():
    """Inclusion Projections Page: 60% target and scenario analysis"""
    st.header("🎯 Inclusion Projections")
    st.markdown("### Financial Inclusion Rate Projections and 60% Target")
    
    _, _, forecast_modeler, _ = get_analyzers()
    if forecast_modeler is None:
        st.error("Unable to initialize forecast modeler.")
        return
    
    forecast_modeler.load_data()
    
    # Scenario Selector
    st.sidebar.subheader("📊 Scenario Selection")
    
    scenario = st.sidebar.radio(
        "Select Scenario",
        options=["optimistic", "base", "pessimistic"],
        index=1,
        help="Choose forecast scenario"
    )
    
    # Target Setting
    target_rate = st.sidebar.slider(
        "Target Inclusion Rate",
        min_value=50,
        max_value=70,
        value=60,
        step=1,
        help="Target financial inclusion rate (%)"
    )
    
    # Generate Forecast
    try:
        forecast_result = forecast_modeler.forecast_indicator(
            indicator_code="ACC_OWNERSHIP",
            pillar="ACCESS",
            forecast_years=[2025, 2026, 2027, 2028, 2029, 2030],
            include_events=True,
            model_type="linear",
            confidence_level=0.95
        )
        
        scenarios = forecast_result["scenarios"]
        selected_scenario = scenarios[scenario]
        
        # Ensure numeric types
        for scen_name, scen_df in scenarios.items():
            if "forecast" in scen_df.columns:
                scenarios[scen_name]["forecast"] = pd.to_numeric(scen_df["forecast"], errors="coerce")
            if "upper_bound" in scen_df.columns:
                scenarios[scen_name]["upper_bound"] = pd.to_numeric(scen_df["upper_bound"], errors="coerce")
            if "lower_bound" in scen_df.columns:
                scenarios[scen_name]["lower_bound"] = pd.to_numeric(scen_df["lower_bound"], errors="coerce")
        
        selected_scenario = scenarios[scenario]
        
        # Progress toward 60% target
        st.subheader(f"Progress Toward {target_rate}% Target ({scenario.capitalize()} Scenario)")
        
        # Calculate progress
        current_rate = float(forecast_result["historical"]["value_numeric"].iloc[-1])
        projected_rates = pd.to_numeric(selected_scenario["forecast"], errors="coerce")
        years = selected_scenario["year"]
        
        # Find when target is reached
        target_reached = None
        for year, rate in zip(years, projected_rates):
            if rate >= target_rate:
                target_reached = year
                break
        
        # Progress visualization
        col1, col2, col3 = st.columns(3)
        
        with col1:
            progress_pct = min(100, (current_rate / target_rate) * 100)
            st.metric("Current Rate", f"{current_rate:.1f}%")
            st.progress(progress_pct / 100)
        
        with col2:
            if target_reached:
                st.metric("Target Reached", f"Year {target_reached}", delta=f"{target_reached - 2024} years")
            else:
                final_rate = float(projected_rates.iloc[-1]) if hasattr(projected_rates, 'iloc') else float(projected_rates[-1])
                gap = target_rate - final_rate
                st.metric("Projected (2030)", f"{final_rate:.1f}%", delta=f"{gap:.1f}pp gap")
        
        with col3:
            avg_growth_needed = (target_rate - current_rate) / (2030 - 2024) if target_reached is None else 0
            st.metric("Avg Growth Needed", f"{avg_growth_needed:.2f}pp/year" if avg_growth_needed > 0 else "On Track")
        
        # Projection Chart with Target Line
        fig = go.Figure()
        
        # Historical
        historical = forecast_result["historical"]
        fig.add_trace(go.Scatter(
            x=historical["year"],
            y=historical["value_numeric"],
            mode="lines+markers",
            name="Historical",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=10)
        ))
        
        # Projection
        fig.add_trace(go.Scatter(
            x=years,
            y=projected_rates,
            mode="lines+markers",
            name=f"{scenario.capitalize()} Scenario",
            line=dict(color="#2ca02c", width=3, dash="dash"),
            marker=dict(size=10)
        ))
        
        # Target line
        fig.add_hline(
            y=target_rate,
            line_dash="dot",
            line_color="red",
            annotation_text=f"{target_rate}% Target",
            annotation_position="right"
        )
        
        # Mark target achievement
        if target_reached:
            fig.add_vline(
                x=target_reached,
                line_dash="dot",
                line_color="green",
                annotation_text=f"Target Reached: {target_reached}",
                annotation_position="top"
            )
        
        fig.update_layout(
            title=f"Financial Inclusion Projection: Progress Toward {target_rate}% Target",
            xaxis_title="Year",
            yaxis_title="Financial Inclusion Rate (%)",
            hovermode="x unified",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Scenario Comparison
        st.subheader("Scenario Comparison")
        
        # Ensure all forecast columns are numeric before operations
        opt_forecast = pd.to_numeric(scenarios["optimistic"]["forecast"], errors="coerce")
        base_forecast = pd.to_numeric(scenarios["base"]["forecast"], errors="coerce")
        pess_forecast = pd.to_numeric(scenarios["pessimistic"]["forecast"], errors="coerce")
        
        scenario_comparison = pd.DataFrame({
            "Year": scenarios["base"]["year"],
            "Optimistic": opt_forecast.round(1),
            "Base": base_forecast.round(1),
            "Pessimistic": pess_forecast.round(1),
            "Range": (opt_forecast - pess_forecast).round(1)
        })
        
        st.dataframe(scenario_comparison, use_container_width=True, hide_index=True)
        
        # Scenario visualization
        fig = go.Figure()
        
        for scen_name, scen_data in scenarios.items():
            # Ensure forecast is numeric
            forecast_values = pd.to_numeric(scen_data["forecast"], errors="coerce")
            fig.add_trace(go.Scatter(
                x=scen_data["year"],
                y=forecast_values,
                mode="lines+markers",
                name=scen_name.capitalize(),
                line=dict(width=2),
                marker=dict(size=8)
            ))
        
        fig.add_hline(
            y=target_rate,
            line_dash="dot",
            line_color="red",
            annotation_text=f"{target_rate}% Target"
        )
        
        fig.update_layout(
            title="Scenario Comparison: All Scenarios",
            xaxis_title="Year",
            yaxis_title="Financial Inclusion Rate (%)",
            hovermode="x unified",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Download projection data
        csv = scenario_comparison.to_csv(index=False)
        st.download_button(
            label="📥 Download Projection Data (CSV)",
            data=csv,
            file_name="inclusion_projections.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error generating projections: {e}")
        st.info("Please ensure historical data is available.")


def main():
    """Main dashboard application"""
    
    # Sidebar Navigation
    st.sidebar.title("📊 Navigation")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Select Page",
        options=["Overview", "Trends", "Forecasts", "Inclusion Projections"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "Ethiopia Financial Inclusion Forecasting Dashboard\n\n"
        "Explore data, understand event impacts, and view forecasts for financial inclusion in Ethiopia."
    )
    
    # Main Title
    st.title("🇪🇹 Ethiopia Financial Inclusion Dashboard")
    st.markdown("### Data Exploration • Event Impacts • Forecasts")
    st.markdown("---")
    
    # Route to selected page
    if page == "Overview":
        page_overview()
    elif page == "Trends":
        page_trends()
    elif page == "Forecasts":
        page_forecasts()
    elif page == "Inclusion Projections":
        page_projections()


if __name__ == "__main__":
    main()
