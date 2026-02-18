# Healthcare Claims Denial Prediction & Revenue Leakage Analyzer

## Objective
Predict high-risk reimbursement outcomes (denial/underpayment proxy) and quantify expected revenue leakage using CMS Medicare Provider & Service utilization/payment data.

## Dataset
CMS Medicare Physician & Other Practitioners (Provider & Service).  
Download from: https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners

> Raw CMS data is not stored in this repo due to file size. Place your CSV in `data/raw/`.

## Workflow
1. Data ingestion & cleaning
2. Feature engineering on billing & reimbursement patterns
3. Denial/underpayment risk modeling (Random Forest baseline)
4. Financial impact analysis
5. BI dashboard specification (Power BI/Tableau)

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
