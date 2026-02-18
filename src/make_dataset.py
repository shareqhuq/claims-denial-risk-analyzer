# src/make_dataset.py

import argparse
from pathlib import Path
import pandas as pd


# Exact CMS column mapping (Title Case version)
COLUMN_MAP = {
    "Rndrng_NPI": "npi",
    "Rndrng_Prvdr_State_Abrvtn": "provider_state",
    "Rndrng_Prvdr_Zip5": "provider_zip",
    "Rndrng_Prvdr_Type": "provider_type",
    "HCPCS_Cd": "hcpcs_code",
    "Place_Of_Srvc": "place_of_service",
    "Tot_Srvcs": "line_srvc_cnt",
    "Tot_Benes": "bene_unique_cnt",
    "Avg_Sbmtd_Chrg": "submitted_charge",
    "Avg_Mdcr_Alowd_Amt": "allowed_amount",
    "Avg_Mdcr_Pymt_Amt": "payment_amount",
}


def load_csv(input_dir: Path) -> pd.DataFrame:
    csvs = list(input_dir.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError("No CSV files found in data/raw")

    file_path = csvs[0]
    print(f"Loading file: {file_path.name}")

    # Load only needed columns (faster for huge CMS files)
    df = pd.read_csv(
        file_path,
        usecols=list(COLUMN_MAP.keys()),
        low_memory=False
    )

    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:

    # Rename columns → standardized schema
    df = df.rename(columns=COLUMN_MAP)

    # Convert financial fields to numeric
    money_cols = [
        "submitted_charge",
        "allowed_amount",
        "payment_amount",
    ]

    for col in money_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows missing CPT / HCPCS
    df = df.dropna(subset=["hcpcs_code"])

    # Feature Engineering
    df["payment_to_charge_ratio"] = (
        df["payment_amount"] / df["submitted_charge"]
    )

    df["charge_payment_gap"] = (
        df["submitted_charge"] - df["payment_amount"]
    )

    df["charge_payment_gap"] = df["charge_payment_gap"].clip(lower=0)

    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--output_path", required=True)
    args = parser.parse_args()

    raw_df = load_csv(Path(args.input_dir))
    clean_df = clean_dataset(raw_df)

    Path(args.output_path).parent.mkdir(parents=True, exist_ok=True)

    clean_df.to_parquet(args.output_path, index=False)

    print("Dataset successfully cleaned and saved.")
    print(f"Rows processed: {len(clean_df):,}")


if __name__ == "__main__":
    main()
