-- Top HCPCS codes by expected leakage
SELECT
  hcpcs_code,
  COUNT(*) AS rows_ct,
  AVG(risk_score) AS avg_risk,
  SUM(expected_leakage) AS expected_leakage
FROM claims_scored
GROUP BY hcpcs_code
ORDER BY expected_leakage DESC
LIMIT 20;

-- Geographic hotspots
SELECT
  provider_state,
  COUNT(*) AS rows_ct,
  AVG(risk_score) AS avg_risk,
  SUM(expected_leakage) AS expected_leakage
FROM claims_scored
GROUP BY provider_state
ORDER BY expected_leakage DESC
LIMIT 20;

-- Specialty/provider type hotspots
SELECT
  provider_type,
  COUNT(*) AS rows_ct,
  AVG(risk_score) AS avg_risk,
  SUM(expected_leakage) AS expected_leakage
FROM claims_scored
GROUP BY provider_type
ORDER BY expected_leakage DESC
LIMIT 20;
