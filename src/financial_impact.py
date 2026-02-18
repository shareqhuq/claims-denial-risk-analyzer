# src/financial_impact.py
import argparse
import pandas as pd
import numpy as np

def estimate_leakage(df: pd.DataFrame) -> pd.DataFrame:
    # Conservative expected leakage:
    # leakage = risk_score * (submitted_charge - payment_amount), clipped at >=0
    gap = (df["submitted_charge"] - df["payment_amount"]).clip(lower=0)
    df["expected_leakage"] = df["risk_score"] * gap
    return df

def top_cuts(df: pd.DataFrame, col: str, n: int = 15) -> pd.DataFrame:
    return (
        df.groupby(col, dropna=False)
          .agg(
              claims=("risk_score", "size"),
              avg_risk=("risk_score", "mean"),
              total_submitted=("submitted_charge", "sum"),
              total_paid=("payment_amount", "sum"),
              expected_leakage=("expected_leakage", "sum"),
          )
          .sort_values("expected_leakage", ascending=False)
          .head(n)
          .reset_index()
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored_path", type=str, required=True)
    ap.add_argument("--report_out", type=str, required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.scored_path, low_memory=False)

    # Basic validation
    needed = {"submitted_charge", "payment_amount", "risk_score"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["submitted_charge"] = pd.to_numeric(df["submitted_charge"], errors="coerce")
    df["payment_amount"] = pd.to_numeric(df["payment_amount"], errors="coerce")
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce")

    df = df.dropna(subset=["submitted_charge", "payment_amount", "risk_score"])
    df = estimate_leakage(df)

    headline = {
        "rows": len(df),
        "total_submitted": df["submitted_charge"].sum(),
        "total_paid": df["payment_amount"].sum(),
        "gross_gap": (df["submitted_charge"] - df["payment_amount"]).clip(lower=0).sum(),
        "expected_leakage": df["expected_leakage"].sum(),
        "avg_risk": df["risk_score"].mean(),
        "pct_high_risk": (df.get("high_risk_flag", 0).astype(int).mean() if "high_risk_flag" in df.columns else np.nan),
    }

    # Breakdowns
    cuts = {}
    for dim in ["hcpcs_code", "provider_state", "provider_type", "place_of_service"]:
        if dim in df.columns:
            cuts[dim] = top_cuts(df, dim, n=15)

    # Write an executive report (markdown)
    lines = []
    lines.append("# Financial Impact Report — Denial/Underpayment Risk\n")
    lines.append("## Executive Summary\n")
    lines.append(f"- Rows analyzed: **{headline['rows']:,}**")
    lines.append(f"- Total submitted charges: **${headline['total_submitted']:,.0f}**")
    lines.append(f"- Total payments: **${headline['total_paid']:,.0f}**")
    lines.append(f"- Gross charge–payment gap (>=0): **${headline['gross_gap']:,.0f}**")
    lines.append(f"- **Expected revenue leakage (risk-weighted): ${headline['expected_leakage']:,.0f}**")
    lines.append(f"- Average risk score: **{headline['avg_risk']:.3f}**")
    if not np.isnan(headline["pct_high_risk"]):
        lines.append(f"- % high-risk (thresholded): **{headline['pct_high_risk']*100:.1f}%**")
    lines.append("\n---\n")

    lines.append("## Top Leakage Drivers (where available)\n")
    for dim, tdf in cuts.items():
        lines.append(f"### {dim}\n")
        lines.append(tdf.to_markdown(index=False))
        lines.append("\n")

    lines.append("\n---\n## Process Improvement Recommendations\n")
    lines.append(
        "- **Pre-submit validation for top leakage HCPCS codes**: build rules for required modifiers, frequency limits, and documentation checklists.\n"
        "- **Prior auth readiness** (if applicable): flag high-risk services for authorization confirmation before billing.\n"
        "- **Payer policy playbooks**: if you have payer mapping internally, align edits to payer-specific rules (LCD/NCD, bundling, MUE edits).\n"
        "- **Coding education loop**: focus training on specialties/procedures with highest expected leakage.\n"
        "- **Geographic variance review**: investigate states/regions with consistently low payment-to-charge ratios for contracting/coding workflow differences.\n"
    )

    with open(args.report_out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote report: {args.report_out}")

if __name__ == "__main__":
    main()
