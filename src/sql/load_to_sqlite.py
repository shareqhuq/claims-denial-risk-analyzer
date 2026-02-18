# src/sql/load_to_sqlite.py
import argparse
import sqlite3
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored_csv", type=str, required=True)
    ap.add_argument("--db_path", type=str, required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.scored_csv, low_memory=False)
    conn = sqlite3.connect(args.db_path)

    # Replace table each time for simplicity
    df.to_sql("claims_scored", conn, if_exists="replace", index=False)

    # Helpful indexes
    cur = conn.cursor()
    for col in ["hcpcs_code", "provider_state", "provider_type", "place_of_service"]:
        if col in df.columns:
            cur.execute(f"CREATE INDEX IF NOT EXISTS idx_claims_{col} ON claims_scored({col});")
    conn.commit()
    conn.close()

    print(f"SQLite DB created: {args.db_path} (table: claims_scored)")

if __name__ == "__main__":
    main()
