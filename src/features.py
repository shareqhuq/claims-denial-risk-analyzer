# src/features.py
import pandas as pd
import numpy as np
from src.utils import safe_divide

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Core ratios
    out["payment_to_charge_ratio"] = safe_divide(out["payment_amount"], out["submitted_charge"])
    if "allowed_amount" in out.columns:
        out["payment_to_allowed_ratio"] = safe_divide(out["payment_amount"], out["allowed_amount"])
        out["allowed_to_charge_ratio"] = safe_divide(out["allowed_amount"], out["submitted_charge"])

    # Procedure "complexity" proxies (heuristics)
    if "line_srvc_cnt" in out.columns:
        out["log_line_srvc_cnt"] = np.log1p(out["line_srvc_cnt"])
    if "bene_unique_cnt" in out.columns:
        out["services_per_bene"] = safe_divide(out.get("line_srvc_cnt", pd.Series([pd.NA]*len(out))), out["bene_unique_cnt"])

    # Geographic patterns
    if "provider_state" in out.columns:
        out["is_high_variance_state"] = out["provider_state"].isin(
            out.groupby("provider_state")["payment_to_charge_ratio"].std(numeric_only=True).sort_values(ascending=False).head(10).index
        ).astype(int)

    # Missingness flags (often predictive)
    for c in ["provider_type", "place_of_service"]:
        if c in out.columns:
            out[f"{c}_missing"] = out[c].isna().astype(int)

    return out
