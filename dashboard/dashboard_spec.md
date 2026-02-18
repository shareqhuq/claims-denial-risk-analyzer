# Executive Dashboard Spec — Claims Denial/Underpayment Risk

## Data Source
Use `data/outputs/claims_scored.csv` (or SQLite table `claims_scored`).

## Core Measures (create in Power BI/Tableau)
- Avg Risk Score = AVG(risk_score)
- Expected Leakage = SUM(expected_leakage)
- Gross Gap = SUM(MAX(submitted_charge - payment_amount, 0))
- High Risk Rate = AVG(high_risk_flag)

## Recommended Pages

### Page 1 — Executive Overview
**Cards**
- Total Submitted
- Total Paid
- Expected Leakage
- Avg Risk Score
- High Risk Rate

**Charts**
- Bar: Expected Leakage by HCPCS (Top 15)
- Bar: Expected Leakage by Provider Type (Top 15)
- Map: Expected Leakage by State

### Page 2 — Procedure & Specialty Drilldown
- Heatmap: Provider Type x HCPCS (color=Expected Leakage, tooltip=Avg Risk)
- Scatter: Submitted Charge vs Payment Amount (size=Expected Leakage, color=Risk)

### Page 3 — Geographic Trends
- Filled map by State (Expected Leakage)
- Table: State, rows, avg risk, expected leakage

## Filters/Slicers
- Provider State
- Provider Type
- Place of Service
- HCPCS Code
- High Risk Flag
