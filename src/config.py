# src/config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    # Proxy-label tuning:
    # Claims are flagged as "denial/underpayment-like" if payment-to-charge ratio is in the bottom X percentile
    UNDERPAYMENT_PERCENTILE: float = 0.10

    # Risk threshold for "high risk" output label
    HIGH_RISK_THRESHOLD: float = 0.70

    # Columns: dataset versions vary, so we map best-effort names in make_dataset.py
    # Keep these for documentation.
    CANONICAL_COLUMNS = (
        "npi",
        "provider_state",
        "provider_zip",
        "provider_type",
        "hcpcs_code",
        "place_of_service",
        "line_srvc_cnt",
        "bene_unique_cnt",
        "submitted_charge",
        "allowed_amount",
        "payment_amount",
    )
