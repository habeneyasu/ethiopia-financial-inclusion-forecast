# Policy Report Generation

## Generate Report

```bash
python generate_policy_report.py
```

The report will be saved to `reports/policy_report.md` with visualizations in `reports/figures/`.

## Report Contents

The policy report includes:

1. **Executive Summary** - Key highlights and policy implications
2. **Key Findings** - 4 major insights with evidence
3. **Data Overview** - 2 tables (Dataset Composition, Data by Pillar)
4. **Access Analysis** - Table 3: Account Ownership Growth trajectory
5. **Usage Analysis** - Key usage indicators table
6. **Event Timeline** - Table 4: Events by category
7. **Correlation Analysis** - Correlation table with Account Ownership
8. **Policy Recommendations** - 5 actionable recommendations
9. **Conclusion** - Key takeaways

## Visualizations

The report references 4 key visualizations:
- Figure 1: Account Ownership Trajectory (2011-2024) with events
- Figure 2: Digital Payment Usage Trends
- Figure 3: Event Timeline
- Figure 4: Indicator Correlation Matrix

Visualizations are saved as HTML (interactive) and PNG (static) files.

## Converting to PDF

To convert the markdown report to PDF:

```bash
# Using pandoc (if installed)
pandoc reports/policy_report.md -o reports/policy_report.pdf --pdf-engine=xelatex

# Or use online tools like:
# - https://www.markdowntopdf.com/
# - https://dillinger.io/
```

## Report Length

The report is designed to be **maximum 8 pages** when converted to PDF, making it concise and impactful for policy makers.
