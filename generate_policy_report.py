#!/usr/bin/env python3
"""
Generate comprehensive policy report for Tasks 1 & 2
Run: python generate_policy_report.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.reports.report_generator import PolicyReportGenerator

if __name__ == "__main__":
    generator = PolicyReportGenerator()
    generator.generate_report()
    print("\n✓ Policy report generated successfully!")
    print(f"  Location: reports/policy_report.md")
    print(f"  Figures: reports/figures/")
