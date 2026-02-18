# src/score_claims.py
import argparse
import joblib
import pandas as pd

from src.config import Settings
from src.features import add_features

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_path", type=str, required=True)
    ap.add_argument("--model_path", type=str, required=True)
    ap.add_argument("--out_path", type=str, required=True)
    args = ap.parse_args()

    df = pd.read_parquet(args.data_path)
    df = add_features(df)

    bundle = joblib.load(args.model_path)
    model = bundle["model"]

    # Build X using the same columns present during training
    feats = bundle["numeric_features"] + bundle["categorical_features"]
    for c in feats:
        if c not in df.columns:
            df[c] = pd.NA

    X = df[feats]
    df["risk_score"] = model.predict_proba(X)[:, 1]
    df["high_risk_flag"] = (df["risk_score"] >= Settings.HIGH_RISK_THRESHOLD).astype(int)

    df.to_csv(args.out_path, index=False)
    print(f"Saved scored claims: {args.out_path} rows={len(df):,}")

if __name__ == "__main__":
    main()
