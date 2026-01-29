#!/usr/bin/env python3
"""
Interactive script to inspect data quality and explore the dataset
Run: python inspect_data_quality.py
"""

from src.data import DataLoader, DataExplorer
from src.utils.config import config
import pandas as pd

def main():
    print("=" * 80)
    print("DATA QUALITY INSPECTION")
    print("=" * 80)
    
    # Initialize
    loader = DataLoader()
    explorer = DataExplorer(loader)
    
    # Load data
    print("\n[1] Loading datasets...")
    datasets = explorer.load_all_data()
    unified_data = datasets["unified_data"]
    impact_links = datasets.get("impact_links", pd.DataFrame())
    reference_codes = datasets.get("reference_codes", pd.DataFrame())
    
    print(f"✓ Loaded {len(unified_data)} records")
    if not impact_links.empty:
        print(f"✓ Loaded {len(impact_links)} impact links")
    if not reference_codes.empty:
        print(f"✓ Loaded {len(reference_codes)} reference codes")
    
    # Basic statistics
    print("\n[2] Dataset Overview")
    print("-" * 80)
    print(f"Total records: {len(unified_data)}")
    print(f"Total columns: {len(unified_data.columns)}")
    print(f"\nColumns: {', '.join(unified_data.columns[:10])}...")
    
    # Record counts
    print("\n[3] Record Type Distribution")
    print("-" * 80)
    counts = explorer.get_record_counts()
    for category, count_series in counts.items():
        print(f"\n{category.upper()}:")
        print(count_series.to_string())
    
    # Temporal analysis
    print("\n[4] Temporal Range")
    print("-" * 80)
    temporal = explorer.get_temporal_range()
    print(f"Date range: {temporal.get('date_range', 'N/A')}")
    print(f"Min date: {temporal.get('min_date', 'N/A')}")
    print(f"Max date: {temporal.get('max_date', 'N/A')}")
    print(f"Date column used: {temporal.get('date_column', 'N/A')}")
    
    # Indicators
    print("\n[5] Unique Indicators")
    print("-" * 80)
    indicators = explorer.get_unique_indicators()
    print(f"Total unique indicators: {len(indicators)}")
    if not indicators.empty:
        print("\nFirst 10 indicators:")
        print(indicators.head(10).to_string())
    
    # Events
    print("\n[6] Events Catalog")
    print("-" * 80)
    events = explorer.get_events_catalog()
    print(f"Total events: {len(events)}")
    if not events.empty:
        print("\nEvents:")
        print(events.to_string())
    
    # Impact links
    print("\n[7] Impact Links Summary")
    print("-" * 80)
    impact_summary = explorer.get_impact_links_summary()
    if impact_summary:
        for key, value in impact_summary.items():
            print(f"{key}: {value}")
    
    # Data quality checks
    print("\n[8] Data Quality Checks")
    print("-" * 80)
    
    # Missing values
    missing = unified_data.isnull().sum()
    missing_pct = (missing / len(unified_data) * 100).round(2)
    print("\nMissing Values (Top 10):")
    missing_df = pd.DataFrame({
        'Missing Count': missing,
        'Missing %': missing_pct
    }).sort_values('Missing Count', ascending=False).head(10)
    print(missing_df.to_string())
    
    # Duplicate check
    duplicates = unified_data.duplicated().sum()
    print(f"\nDuplicate records: {duplicates}")
    
    # Value ranges for numeric columns
    numeric_cols = unified_data.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        print(f"\nNumeric Columns Summary:")
        print(unified_data[numeric_cols].describe().to_string())
    
    # Confidence levels
    if 'confidence' in unified_data.columns:
        print("\n[9] Confidence Level Distribution")
        print("-" * 80)
        print(unified_data['confidence'].value_counts().to_string())
    
    # Source types
    if 'source_type' in unified_data.columns:
        print("\n[10] Source Type Distribution")
        print("-" * 80)
        print(unified_data['source_type'].value_counts().to_string())
    
    print("\n" + "=" * 80)
    print("Inspection complete! Check reports/task1_exploration_report.txt for full report")
    print("=" * 80)

if __name__ == "__main__":
    main()
