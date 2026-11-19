import pandas as pd


def kpis(frame: pd.DataFrame) -> dict:
    sales = float(frame["Sales"].sum())
    profit = float(frame["Profit"].sum())
    orders = int(frame["Order ID"].nunique())
    customers = int(frame["Customer ID"].nunique())
    return {
        "Revenue": sales,
        "Profit": profit,
        "Orders": orders,
        "AOV": sales / orders if orders else 0,
        "Profit Margin": profit / sales if sales else 0,
        "Customers": customers,
    }


def monthly_trend(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.groupby("Month", observed=True).agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    return result.sort_values("Month")


def discount_profitability(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.assign(Discount_Band=pd.cut(
        frame["Discount"], bins=[-0.001, 0, 0.1, 0.2, 0.3, 0.5, 1],
        labels=["0%", "1-10%", "11-20%", "21-30%", "31-50%", ">50%"]
    )).groupby("Discount_Band", observed=True).agg(
        Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")
    ).reset_index()
