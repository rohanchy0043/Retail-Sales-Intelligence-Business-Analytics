from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = {
    "Order ID", "Order Date", "Ship Date", "Customer ID", "Customer Name",
    "Segment", "Region", "State", "City", "Category", "Sub-Category",
    "Product Name", "Sales", "Quantity", "Discount", "Profit",
    "Ship Mode",
}


def load_data(path: str | Path) -> pd.DataFrame:
    """Load a CSV and validate the core retail analytics schema."""
    frame = pd.read_csv(path)
    missing = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    return frame


def load_cleaned_data(data_dir: str | Path = "data/processed") -> pd.DataFrame:
    root = Path(__file__).resolve().parents[1]
    path = root / data_dir / "cleaned_superstore.csv"
    return load_data(path)
