import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import REQUIRED_COLUMNS


def clean_retail_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    original_rows = len(frame)
    audit = {
        "source_rows": original_rows,
        "missing_values_removed": {},
        "duplicate_rows_removed": 0,
        "invalid_rows_removed": {},
    }
    clean = frame.copy()

    text_columns = ["Segment", "Region", "State", "City", "Category", "Sub-Category", "Ship Mode"]
    for column in text_columns:
        if column in clean:
            clean[column] = clean[column].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    if "Region" in clean:
        clean["Region"] = clean["Region"].replace(
            {"south": "South", "SOUTH": "South", "east": "East", "west": "West", "central": "Central"}
        )

    for column in ["Order Date", "Ship Date"]:
        clean[column] = pd.to_datetime(clean[column], errors="coerce")
    clean["Order Date"] = clean["Order Date"].dt.normalize()
    clean["Ship Date"] = clean["Ship Date"].dt.normalize()

    for column in ["Sales", "Quantity", "Discount", "Profit"]:
        if column in clean:
            clean[column] = pd.to_numeric(clean[column], errors="coerce")

    missing_before = int(clean.isna().sum().sum())
    clean = clean.dropna(subset=["Order ID", "Order Date", "Sales", "Quantity", "Profit"])
    audit["missing_values_removed"]["rows_removed_for_required_missing"] = missing_before - int(clean.isna().sum().sum())

    duplicates = int(clean.duplicated().sum())
    clean = clean.drop_duplicates()
    audit["duplicate_rows_removed"] = duplicates

    negative_sales = int((clean["Sales"] < 0).sum())
    clean = clean.loc[clean["Sales"] >= 0].copy()
    audit["invalid_rows_removed"]["negative_sales"] = negative_sales

    impossible_quantity = int((clean["Quantity"] <= 0).sum())
    clean = clean.loc[clean["Quantity"] > 0].copy()
    audit["invalid_rows_removed"]["non_positive_quantity"] = impossible_quantity

    invalid_dates = int(((clean["Ship Date"].notna()) & (clean["Ship Date"] < clean["Order Date"])).sum())
    if invalid_dates:
        clean.loc[clean["Ship Date"] < clean["Order Date"], "Ship Date"] = pd.NaT
    audit["invalid_rows_removed"]["ship_before_order_dates_flagged"] = invalid_dates

    clean["Quantity"] = clean["Quantity"].astype(int)
    if "Discount" in clean:
        clean["Discount"] = clean["Discount"].clip(lower=0, upper=1).fillna(0)
    else:
        clean["Discount"] = 0.0
    clean["Year"] = clean["Order Date"].dt.year
    clean["Month"] = clean["Order Date"].dt.to_period("M").astype(str)
    clean["Quarter"] = clean["Order Date"].dt.to_period("Q").astype(str)
    clean["Delivery Days"] = (clean["Ship Date"] - clean["Order Date"]).dt.days
    clean["Profit Margin"] = np.where(clean["Sales"] != 0, clean["Profit"] / clean["Sales"], 0)
    audit["cleaned_rows"] = len(clean)
    audit["rows_removed"] = original_rows - len(clean)
    audit["cleaning_decisions"] = [
        "Trimmed and standardized text fields.",
        "Converted date and numeric fields; invalid required values were excluded.",
        "Removed exact duplicate rows.",
        "Excluded negative sales and non-positive quantities.",
        "Ship dates earlier than order dates were set to missing rather than deleted.",
        "Added Year, Month, Quarter, Delivery Days, and Profit Margin fields.",
    ]
    return clean, audit


def build_quality_report(audit: dict) -> str:
    lines = [
        "# Data Quality Report",
        "",
        "## Dataset status",
        f"- Source rows: **{audit['source_rows']:,}**",
        f"- Cleaned rows: **{audit['cleaned_rows']:,}**",
        f"- Rows removed or unavailable for required analysis: **{audit['rows_removed']:,}**",
        "",
        "## Cleaning actions",
    ]
    lines.extend(f"- {item}" for item in audit["cleaning_decisions"])
    lines.extend([
        "",
        "## Impact",
        f"- Duplicate rows removed: {audit['duplicate_rows_removed']:,}",
        f"- Negative-sales rows removed: {audit['invalid_rows_removed'].get('negative_sales', 0):,}",
        f"- Non-positive-quantity rows removed: {audit['invalid_rows_removed'].get('non_positive_quantity', 0):,}",
        f"- Ship-before-order dates corrected to missing: {audit['invalid_rows_removed'].get('ship_before_order_dates_flagged', 0):,}",
        "",
        "No source records are silently deleted: every exclusion category is documented above.",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=r"data/raw/superstore/Sample - Superstore.csv")
    parser.add_argument("--output", default="data/processed/cleaned_superstore.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    input_path = root / args.input
    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        frame = pd.read_csv(input_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        frame = pd.read_csv(input_path, encoding="latin1")
    clean, audit = clean_retail_data(frame)
    clean.to_csv(output_path, index=False)
    (root / "reports" / "data_quality_report.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "reports" / "data_quality_report.md").write_text(build_quality_report(audit), encoding="utf-8")
    (root / "reports" / "data_quality_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"Cleaned {len(clean):,} rows; wrote {output_path.relative_to(root)}")


if __name__ == "__main__":
    main()
