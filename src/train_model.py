# src/train_model.py
import argparse
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.ensemble import RandomForestClassifier

from src.config import Settings
from src.features import add_features

def build_proxy_label(df: pd.DataFrame, underpayment_percentile: float) -> pd.Series:
    # Proxy label: bottom X% of payment_to_charge_ratio treated as "denial/underpayment-like"
    ratio = df["payment_to_charge_ratio"].astype(float)
    cutoff = np.nanquantile(ratio, underpayment_percentile)
    y = (ratio <= cutoff).astype(int)
    return y

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_path", type=str, required=True)
    ap.add_argument("--model_out", type=str, required=True)
    args = ap.parse_args()

    df = pd.read_parquet(args.data_path)
    df = add_features(df)

    # Drop rows where ratio cannot be computed
    df = df.dropna(subset=["payment_to_charge_ratio"])

    y = build_proxy_label(df, Settings.UNDERPAYMENT_PERCENTILE)

    # Feature selection
    numeric_features = [
        c for c in df.columns
        if c in {
            "submitted_charge","allowed_amount","payment_amount",
            "payment_to_charge_ratio","payment_to_allowed_ratio","allowed_to_charge_ratio",
            "line_srvc_cnt","bene_unique_cnt","log_line_srvc_cnt","services_per_bene",
            "is_high_variance_state","provider_type_missing","place_of_service_missing"
        } and c in df.columns
    ]
    categorical_features = [c for c in ["provider_state","provider_type","hcpcs_code","place_of_service"] if c in df.columns]

    X = df[numeric_features + categorical_features].copy()

    pre = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    clf = RandomForestClassifier(
        n_estimators=400,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
        min_samples_leaf=5
    )

    pipe = Pipeline([("pre", pre), ("clf", clf)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe.fit(X_train, y_train)

    proba = pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    print(f"ROC AUC: {auc:.4f}")

    preds = (proba >= 0.5).astype(int)
    print(classification_report(y_test, preds, digits=4))

    joblib.dump(
        {"model": pipe, "numeric_features": numeric_features, "categorical_features": categorical_features},
        args.model_out
    )
    print(f"Saved model bundle: {args.model_out}")

if __name__ == "__main__":
    main()
