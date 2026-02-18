# Build Steps (Power BI or Tableau)

## Option A — CSV
1. Import `data/outputs/claims_scored.csv`
2. Ensure numeric types: submitted_charge, allowed_amount, payment_amount, risk_score, expected_leakage
3. Create measures:
   - Expected Leakage = SUM(expected_leakage)
   - Avg Risk Score = AVERAGE(risk_score)
   - High Risk Rate = AVERAGE(high_risk_flag)

## Option B — SQLite
1. Connect to `data/outputs/claims.db`
2. Select table `claims_scored`
3. Same measures as above

## Visuals to create
- Map: Location=provider_state, Color=Expected Leakage
- Bar charts: Expected Leakage by hcpcs_code, provider_type
- Heatmap: provider_type (rows) x hcpcs_code (cols), Color=Expected Leakage
- Distribution: Histogram of risk_score (bin)
