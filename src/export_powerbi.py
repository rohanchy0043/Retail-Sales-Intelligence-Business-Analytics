from pathlib import Path
import pandas as pd


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "data" / "processed" / "cleaned_superstore.csv"
    target = root / "data" / "processed" / "powerbi_export.csv"
    frame = pd.read_csv(source)
    frame.to_csv(target, index=False)
    print(f"Wrote Power BI-ready CSV: {target.relative_to(root)}")


if __name__ == "__main__":
    main()
