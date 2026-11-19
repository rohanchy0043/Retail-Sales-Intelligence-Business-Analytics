import numpy as np
import pandas as pd


def rfm_segmentation(frame: pd.DataFrame, snapshot_date=None) -> pd.DataFrame:
    required = {"Customer ID", "Order ID", "Order Date", "Sales"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing RFM columns: {', '.join(sorted(missing))}")
    if frame.empty:
        return pd.DataFrame(columns=[
            "Customer ID", "Customer Name", "Recency", "Frequency", "Monetary",
            "R Score", "F Score", "M Score", "RFM Segment",
        ])

    data = frame.copy()
    data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")
    data = data.dropna(subset=["Customer ID", "Order ID", "Order Date", "Sales"])
    if data.empty:
        return pd.DataFrame(columns=[
            "Customer ID", "Customer Name", "Recency", "Frequency", "Monetary",
            "R Score", "F Score", "M Score", "RFM Segment",
        ])

    as_of = pd.Timestamp(snapshot_date) if snapshot_date is not None else data["Order Date"].max() + pd.Timedelta(days=1)
    aggregations = {
        "Recency": ("Order Date", lambda dates: int((as_of - dates.max()).days)),
        "Frequency": ("Order ID", "nunique"),
        "Monetary": ("Sales", "sum"),
    }
    if "Customer Name" in data:
        aggregations["Customer Name"] = ("Customer Name", "first")
    rfm = data.groupby("Customer ID", observed=True).agg(**aggregations).reset_index()

    count = len(rfm)
    ranks = rfm[["Recency", "Frequency", "Monetary"]].rank(method="first", pct=True)
    scores = np.ceil(ranks * 4).clip(1, 4).astype(int)
    rfm["R Score"] = 5 - scores["Recency"]
    rfm["F Score"] = scores["Frequency"]
    rfm["M Score"] = scores["Monetary"]
    if count == 1:
        rfm[["R Score", "F Score", "M Score"]] = 3

    def label(row):
        r_score, f_score, m_score = row["R Score"], row["F Score"], row["M Score"]
        if r_score >= 3 and f_score >= 3 and m_score >= 3:
            return "Champions"
        if r_score >= 3 and f_score >= 3:
            return "Loyal Customers"
        if r_score <= 2 and f_score >= 3:
            return "At Risk"
        if r_score == 4 and f_score == 1:
            return "New Customers"
        if r_score <= 2 and f_score <= 2 and m_score <= 2:
            return "Hibernating"
        if r_score >= 3 and f_score >= 2:
            return "Potential Loyalists"
        return "Needs Attention"

    rfm["RFM Segment"] = rfm.apply(label, axis=1)
    return rfm.sort_values(["Monetary", "Frequency"], ascending=False).reset_index(drop=True)
