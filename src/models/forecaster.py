"""
Forecasting Module
Forecasts Account Ownership (Access) and Digital Payment Usage
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy import stats
from src.utils.logger import get_logger
from src.data.loader import DataLoader
from src.data.explorer import DataExplorer
from src.analysis.eda import EDAAnalyzer
from src.models.event_impact import EventImpactModeler

logger = get_logger(__name__)


class ForecastModeler:
    """Class for forecasting financial inclusion indicators"""

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        data_explorer: Optional[DataExplorer] = None,
        eda_analyzer: Optional[EDAAnalyzer] = None,
        event_modeler: Optional[EventImpactModeler] = None
    ):
        """
        Initialize ForecastModeler

        Args:
            data_loader: DataLoader instance
            data_explorer: DataExplorer instance
            eda_analyzer: EDAAnalyzer instance
            event_modeler: EventImpactModeler instance
        """
        self.data_loader = data_loader or DataLoader()
        self.data_explorer = data_explorer or DataExplorer(self.data_loader)
        self.eda_analyzer = eda_analyzer or EDAAnalyzer(self.data_loader, self.data_explorer)
        self.event_modeler = event_modeler or EventImpactModeler(self.data_loader, self.data_explorer)
        self.logger = get_logger(__name__)
        self._datasets: Optional[Dict[str, pd.DataFrame]] = None
        self._historical_data: Optional[Dict[str, pd.DataFrame]] = None

    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load all datasets"""
        if self._datasets is None:
            self._datasets = self.data_explorer.load_all_data()
        return self._datasets

    def get_historical_series(
        self,
        indicator_code: str,
        pillar: str = "ACCESS"
    ) -> pd.DataFrame:
        """
        Extract historical time series for a specific indicator

        Args:
            indicator_code: Indicator code (e.g., 'ACC_OWNERSHIP', 'USG_DIGITAL_PAY')
            pillar: Pillar name (ACCESS, USAGE, etc.)

        Returns:
            DataFrame with year and value_numeric columns
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        self.logger.info(f"Extracting historical series for {indicator_code}")

        # Filter for observations of the specified indicator
        indicator_data = unified_data[
            (unified_data["record_type"] == "observation") &
            (unified_data["pillar"] == pillar) &
            (unified_data["indicator_code"] == indicator_code)
        ].copy()

        if indicator_data.empty:
            self.logger.warning(f"No data found for {indicator_code}")
            return pd.DataFrame()

        # Extract year and value
        date_col = "observation_date"
        if date_col in indicator_data.columns:
            indicator_data["year"] = pd.to_datetime(
                indicator_data[date_col], errors="coerce"
            ).dt.year
        else:
            return pd.DataFrame()

        # Get latest value per year
        series = indicator_data.groupby("year")["value_numeric"].last().reset_index()
        series = series.sort_values("year").dropna()

        return series

    def fit_trend_model(
        self,
        series: pd.DataFrame,
        model_type: str = "linear"
    ) -> Tuple[object, np.ndarray, Dict]:
        """
        Fit trend regression model

        Args:
            series: DataFrame with 'year' and 'value_numeric' columns
            model_type: 'linear' or 'log'

        Returns:
            Tuple of (model, predictions, metrics)
        """
        if series.empty or len(series) < 2:
            raise ValueError("Insufficient data for trend modeling")

        X = series["year"].values.reshape(-1, 1)
        y = series["value_numeric"].values

        if model_type == "linear":
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
        elif model_type == "log":
            # Log-linear model: log(y) = a + b*x
            y_log = np.log(y + 1)  # Add 1 to avoid log(0)
            model = LinearRegression()
            model.fit(X, y_log)
            y_pred_log = model.predict(X)
            y_pred = np.exp(y_pred_log) - 1
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

        # Calculate metrics
        residuals = y - y_pred
        rmse = np.sqrt(np.mean(residuals**2))
        mae = np.mean(np.abs(residuals))
        r2 = model.score(X, y) if model_type == "linear" else None

        metrics = {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "model_type": model_type
        }

        return model, y_pred, metrics

    def forecast_trend(
        self,
        model: object,
        series: pd.DataFrame,
        forecast_years: List[int],
        model_type: str = "linear",
        confidence_level: float = 0.95
    ) -> pd.DataFrame:
        """
        Generate trend-based forecasts with confidence intervals

        Args:
            model: Fitted model
            series: Historical series
            forecast_years: List of years to forecast
            model_type: 'linear' or 'log'
            confidence_level: Confidence level for intervals (default 0.95)

        Returns:
            DataFrame with forecasts and confidence intervals
        """
        X_hist = series["year"].values.reshape(-1, 1)
        y_hist = series["value_numeric"].values

        # Generate predictions
        X_forecast = np.array(forecast_years).reshape(-1, 1)

        if model_type == "linear":
            y_forecast = model.predict(X_forecast)
            # Ensure y_forecast is a numpy array
            y_forecast = np.array(y_forecast).flatten()
            # Calculate prediction intervals
            residuals = y_hist - model.predict(X_hist)
            std_error = np.std(residuals)
            t_critical = stats.t.ppf((1 + confidence_level) / 2, len(series) - 2)
            # Ensure X_hist.mean() returns a scalar
            X_hist_mean = float(X_hist.mean())
            se_pred = std_error * np.sqrt(1 + 1/len(series) + (X_forecast - X_hist_mean)**2 / np.sum((X_hist - X_hist_mean)**2))
            margin = t_critical * se_pred.flatten()
        else:  # log model
            y_forecast_log = model.predict(X_forecast)
            y_forecast = np.exp(y_forecast_log) - 1
            # Ensure y_forecast is a numpy array
            y_forecast = np.array(y_forecast).flatten()
            # Simplified confidence intervals for log model
            residuals = np.log(y_hist + 1) - model.predict(X_hist)
            std_error = np.std(residuals)
            t_critical = stats.t.ppf((1 + confidence_level) / 2, len(series) - 2)
            margin = t_critical * std_error * np.ones(len(forecast_years))
            margin = y_forecast * (np.exp(margin) - 1)  # Approximate

        # Ensure margin is a numpy array
        margin = np.array(margin).flatten()
        
        forecasts = pd.DataFrame({
            "year": forecast_years,
            "forecast": y_forecast,
            "lower_bound": y_forecast - margin,
            "upper_bound": y_forecast + margin,
            "confidence_level": confidence_level
        })

        # Ensure bounds are reasonable (non-negative, within 0-100 for percentages)
        forecasts["lower_bound"] = forecasts["lower_bound"].clip(lower=0, upper=100)
        forecasts["upper_bound"] = forecasts["upper_bound"].clip(lower=0, upper=100)
        forecasts["forecast"] = forecasts["forecast"].clip(lower=0, upper=100)

        return forecasts

    def apply_event_effects(
        self,
        baseline_forecast: pd.DataFrame,
        events: pd.DataFrame,
        impact_links: pd.DataFrame,
        indicator_code: str
    ) -> pd.DataFrame:
        """
        Augment baseline forecast with event effects

        Args:
            baseline_forecast: Baseline trend forecast
            events: Events DataFrame
            impact_links: Impact links DataFrame
            indicator_code: Target indicator code

        Returns:
            Forecast DataFrame with event effects applied
        """
        forecast_with_events = baseline_forecast.copy()
        forecast_with_events["event_effect"] = 0.0

        # Filter impact links for this indicator
        relevant_links = impact_links[
            impact_links["related_indicator"] == indicator_code
        ]

        if relevant_links.empty:
            self.logger.info(f"No impact links found for {indicator_code}")
            return forecast_with_events

        # Get event dates
        for _, link in relevant_links.iterrows():
            parent_id = link.get("parent_id")
            if pd.isna(parent_id):
                continue

            # Find corresponding event
            event = events[events["record_id"] == parent_id]
            if event.empty:
                continue

            event_date = pd.to_datetime(event["observation_date"].iloc[0], errors="coerce")
            if pd.isna(event_date):
                continue

            event_year = event_date.year
            impact_direction = link.get("impact_direction", "increase")
            impact_magnitude = link.get("impact_magnitude", 0.0)
            lag_months = link.get("lag_months", 0)

            # Ensure impact_magnitude is numeric
            try:
                impact_magnitude = float(impact_magnitude) if impact_magnitude is not None else 0.0
            except (ValueError, TypeError):
                impact_magnitude = 0.0

            # Ensure lag_months is numeric
            try:
                lag_months = int(lag_months) if lag_months is not None else 0
            except (ValueError, TypeError):
                lag_months = 0

            # Apply effect to forecast years after event
            for idx, row in forecast_with_events.iterrows():
                forecast_year = row["year"]
                months_after_event = (forecast_year - event_year) * 12 - lag_months

                if months_after_event > 0:
                    # Gradual effect (distributed over time)
                    effect_strength = min(1.0, months_after_event / 24)  # Full effect after 24 months
                    effect = impact_magnitude * effect_strength

                    if impact_direction == "decrease":
                        effect = -effect

                    forecast_with_events.at[idx, "event_effect"] += effect

        # Apply event effects to forecast
        forecast_with_events["forecast"] = (
            forecast_with_events["forecast"] + forecast_with_events["event_effect"]
        )
        forecast_with_events["forecast"] = forecast_with_events["forecast"].clip(lower=0, upper=100)

        return forecast_with_events

    def generate_scenarios(
        self,
        base_forecast: pd.DataFrame,
        optimistic_multiplier: float = 1.2,
        pessimistic_multiplier: float = 0.8
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate optimistic, base, and pessimistic scenarios

        Args:
            base_forecast: Base forecast DataFrame
            optimistic_multiplier: Multiplier for optimistic scenario
            pessimistic_multiplier: Multiplier for pessimistic scenario

        Returns:
            Dictionary with scenario forecasts
        """
        scenarios = {}

        # Create a copy and ensure numeric types BEFORE any operations
        base_forecast_clean = base_forecast.copy()
        numeric_cols = ["forecast", "lower_bound", "upper_bound"]
        for col in numeric_cols:
            if col in base_forecast_clean.columns:
                base_forecast_clean[col] = pd.to_numeric(base_forecast_clean[col], errors="coerce")

        # Base scenario
        scenarios["base"] = base_forecast_clean.copy()

        # Ensure we're working with numeric Series (use cleaned version)
        forecast_series = pd.to_numeric(base_forecast_clean["forecast"], errors="coerce")
        upper_series = None
        lower_series = None
        
        if "upper_bound" in base_forecast_clean.columns:
            upper_series = pd.to_numeric(base_forecast_clean["upper_bound"], errors="coerce")
        
        if "lower_bound" in base_forecast_clean.columns:
            lower_series = pd.to_numeric(base_forecast_clean["lower_bound"], errors="coerce")

        # Optimistic scenario
        optimistic = base_forecast_clean.copy()
        optimistic["forecast"] = (forecast_series * optimistic_multiplier).clip(lower=0, upper=100)
        
        if upper_series is not None:
            optimistic["upper_bound"] = (upper_series * optimistic_multiplier).clip(lower=0, upper=100)
        
        if lower_series is not None:
            optimistic["lower_bound"] = (lower_series * optimistic_multiplier).clip(lower=0, upper=100)
        
        scenarios["optimistic"] = optimistic

        # Pessimistic scenario
        pessimistic = base_forecast_clean.copy()
        pessimistic["forecast"] = (forecast_series * pessimistic_multiplier).clip(lower=0, upper=100)
        
        if upper_series is not None:
            pessimistic["upper_bound"] = (upper_series * pessimistic_multiplier).clip(lower=0, upper=100)
        
        if lower_series is not None:
            pessimistic["lower_bound"] = (lower_series * pessimistic_multiplier).clip(lower=0, upper=100)
        
        scenarios["pessimistic"] = pessimistic

        return scenarios

    def forecast_indicator(
        self,
        indicator_code: str,
        pillar: str,
        forecast_years: List[int],
        include_events: bool = True,
        model_type: str = "linear",
        confidence_level: float = 0.95
    ) -> Dict:
        """
        Complete forecasting pipeline for an indicator

        Args:
            indicator_code: Indicator code to forecast
            pillar: Pillar name
            forecast_years: Years to forecast
            include_events: Whether to include event effects
            model_type: 'linear' or 'log'
            confidence_level: Confidence level for intervals

        Returns:
            Dictionary with forecasts, scenarios, and metadata
        """
        self.logger.info(f"Forecasting {indicator_code} for years {forecast_years}")

        # Get historical data
        historical = self.get_historical_series(indicator_code, pillar)
        if historical.empty:
            raise ValueError(f"No historical data for {indicator_code}")

        # Fit trend model
        model, y_pred, metrics = self.fit_trend_model(historical, model_type)

        # Generate baseline forecast
        baseline = self.forecast_trend(
            model, historical, forecast_years, model_type, confidence_level
        )

        # Apply event effects if requested
        if include_events:
            if self._datasets is None:
                self.load_data()

            events = self._datasets["unified_data"][
                self._datasets["unified_data"]["record_type"] == "event"
            ]
            impact_links = self._datasets.get("impact_links", pd.DataFrame())

            forecast_with_events = self.apply_event_effects(
                baseline, events, impact_links, indicator_code
            )
        else:
            forecast_with_events = baseline.copy()

        # Generate scenarios
        scenarios = self.generate_scenarios(forecast_with_events)

        return {
            "indicator_code": indicator_code,
            "pillar": pillar,
            "historical": historical,
            "baseline": baseline,
            "forecast": forecast_with_events,
            "scenarios": scenarios,
            "model_metrics": metrics,
            "model_type": model_type
        }

    def generate_forecast_table(
        self,
        forecast_results: Dict,
        scenario: str = "base"
    ) -> pd.DataFrame:
        """
        Generate formatted forecast table

        Args:
            forecast_results: Results from forecast_indicator
            scenario: Scenario to use ('base', 'optimistic', 'pessimistic')

        Returns:
            Formatted DataFrame
        """
        forecast_df = forecast_results["scenarios"][scenario].copy()

        # Ensure numeric types
        forecast_vals = pd.to_numeric(forecast_df["forecast"], errors="coerce")
        lower_vals = pd.to_numeric(forecast_df["lower_bound"], errors="coerce")
        upper_vals = pd.to_numeric(forecast_df["upper_bound"], errors="coerce")

        table = pd.DataFrame({
            "Year": forecast_df["year"],
            "Forecast (%)": forecast_vals.round(1),
            "Lower Bound (%)": lower_vals.round(1),
            "Upper Bound (%)": upper_vals.round(1),
            "Range": (upper_vals - lower_vals).round(1)
        })

        return table
