# Project 2: Exploratory Data Analysis (DecodeLabs Data Analytics, Batch 2026)

**Question:** Which patterns, trends and outliers in the orders data are worth acting on, and which are noise?

**Data:** Cleaned output of Project 1 (1,200 orders, Jan 2023 to Jun 2025, 0 nulls, 0 duplicates).

## Headline findings
- Monthly order value fell about 16% (2023 to 2025 H1); trend is downward but not yet statistically significant (p = 0.11).
- 41.4% of orders are Cancelled or Returned (about $520K); rate rose from 39.2% (2024) to 46.8% (2025 H1).
- Order value is right-skewed: median $824 vs mean $1,054. Top 10% of orders = 26% of value.
- 8 IQR outliers, all Quantity = 5 bulk orders: real transactions, kept.
- Product, payment, coupon and referral do not change order value (all p > 0.4).

## Files
- `EDA_Report_Project2.pdf`: executive summary + findings
- `EDA_Statistics.xlsx`: all statistics tables
- `eda_analysis.py`: statistics and charts; `build_report.py`: PDF
- `charts/`: PNG charts

## Run
    pip install pandas scipy matplotlib openpyxl reportlab pillow
    python eda_analysis.py Cleaned_Dataset.csv out
    python build_report.py out

## Limitations
No cost, margin, discount amount or return-reason fields; 2025 covers Jan-Jun only.
