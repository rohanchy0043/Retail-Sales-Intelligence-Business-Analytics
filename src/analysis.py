import calendar

import pandas as pd


def kpis(frame: pd.DataFrame) -> dict:
    sales = float(frame["Sales"].sum())
    profit = float(frame["Profit"].sum())
    orders = int(frame["Order ID"].nunique())
    customers = int(frame["Customer ID"].nunique())
    result = {
        "Revenue": sales,
        "Profit": profit,
        "Orders": orders,
        "AOV": sales / orders if orders else 0,
        "Profit Margin": profit / sales if sales else 0,
        "Customers": customers,
    }
    if "Month" in frame and not frame.empty:
        monthly_sales = frame.groupby("Month", observed=True)["Sales"].sum().sort_index()
        result["Sales Growth"] = (
            float(monthly_sales.iloc[-1] / monthly_sales.iloc[-2] - 1)
            if len(monthly_sales) >= 2 and monthly_sales.iloc[-2] != 0
            else None
        )
    else:
        result["Sales Growth"] = None
    return result


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


def monthly_seasonality(frame: pd.DataFrame) -> pd.DataFrame:
    if "Order Date" not in frame or frame.empty:
        return pd.DataFrame(columns=["Month Name", "Average Revenue", "Seasonality Index"])
    data = frame.assign(
        Month_Number=pd.to_datetime(frame["Order Date"]).dt.month,
        Year_Number=pd.to_datetime(frame["Order Date"]).dt.year,
    )
    monthly_revenue = data.groupby(["Year_Number", "Month_Number"], observed=True)["Sales"].sum()
    average_by_month = monthly_revenue.groupby("Month_Number").mean()
    overall_average = monthly_revenue.mean()
    result = average_by_month.rename("Average Revenue").reset_index()
    result["Seasonality Index"] = result["Average Revenue"] / overall_average if overall_average else 0
    result["Month Name"] = result["Month_Number"].map(lambda month: calendar.month_abbr[month])
    return result.sort_values("Month_Number")[["Month Name", "Average Revenue", "Seasonality Index"]]
