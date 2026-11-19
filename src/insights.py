import pandas as pd


def build_insights(frame: pd.DataFrame) -> dict[str, list[str]]:
    observations = []
    recommendations = []

    region = frame.groupby("Region", observed=True)["Profit"].sum().sort_values(ascending=False)
    if not region.empty:
        observations.append(f"{region.index[0]} is the most profitable region, contributing {region.iloc[0]:,.2f} in profit.")
        recommendations.append(f"Prioritize inventory and marketing in {region.index[0]} while auditing the lowest-profit region.")

    category = frame.groupby("Category", observed=True)["Profit"].sum().sort_values(ascending=False)
    if not category.empty:
        observations.append(f"{category.index[0]} is the highest-profit category at {category.iloc[0]:,.2f}.")
        recommendations.append("Protect winning category margins through focused assortment and targeted promotions.")

    segment = frame.groupby("Segment", observed=True)["Sales"].sum().sort_values(ascending=False)
    if not segment.empty:
        observations.append(f"{segment.index[0]} contributes the most segment revenue: {segment.iloc[0]:,.2f}.")
        recommendations.append("Retain high-revenue segments with loyalty actions and avoid blanket discounting.")

    monthly = frame.groupby("Month", observed=True)["Sales"].sum()
    if not monthly.empty:
        month = monthly.idxmax()
        observations.append(f"The highest-sales month is {month}, with {monthly.loc[month]:,.2f} in revenue.")

    loss_products = frame.groupby("Product Name", observed=True)["Profit"].sum()
    loss_products = loss_products[loss_products < 0].sort_values()
    if not loss_products.empty:
        observations.append(f"{len(loss_products)} products generate negative profit; the largest loss is {loss_products.index[0]}.")
        recommendations.append("Review pricing, discounts, freight, and sourcing for loss-making products.")
    else:
        observations.append("No products have negative total profit in the current filtered view.")

    return {"observations": observations, "recommendations": recommendations}
