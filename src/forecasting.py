from pathlib import Path
import numpy as np
import pandas as pd


def evaluate_monthly_forecast(frame: pd.DataFrame, holdout_months: int = 3) -> dict:
    monthly = frame.groupby("Month", observed=True)["Sales"].sum().sort_index().astype(float)
    if len(monthly) <= holdout_months:
        raise ValueError(f"At least {holdout_months + 1} monthly periods are required for holdout evaluation.")

    values = monthly.to_numpy()
    split = len(values) - holdout_months
    train = values[:split]
    actual = values[split:]
    train_x = np.arange(len(train), dtype=float)
    slope, intercept = np.polyfit(train_x, train, 1)
    test_x = np.arange(len(train), len(values), dtype=float)
    predicted = np.maximum(intercept + slope * test_x, 0)
    naive = np.repeat(train[-1], len(actual))
    mae = float(np.mean(np.abs(actual - predicted)))
    mape = float(np.mean(np.abs((actual - predicted) / actual)) * 100) if np.all(actual != 0) else None
    naive_mae = float(np.mean(np.abs(actual - naive)))
    return {
        "holdout_months": holdout_months,
        "actual": actual,
        "predicted": predicted,
        "periods": monthly.index[split:].tolist(),
        "mae": mae,
        "mape": mape,
        "naive_mae": naive_mae,
    }


def forecast_monthly_sales(frame: pd.DataFrame, periods: int = 3) -> tuple[pd.DataFrame, dict]:
    monthly = frame.groupby("Month", observed=True)["Sales"].sum().sort_index()
    y = monthly.astype(float).to_numpy()
    if len(y) < 2:
        raise ValueError("At least two monthly periods are required.")
    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = intercept + slope * x
    residual_std = float(np.std(y - fitted, ddof=1)) if len(y) > 1 else 0.0
    future_x = np.arange(len(y), len(y) + periods)
    forecast = intercept + slope * future_x
    last_period = pd.Period(monthly.index[-1], freq="M")
    future_months = [str(last_period + i) for i in range(1, periods + 1)]

    actual = pd.DataFrame({"Period": monthly.index, "Actual": y, "Type": "Actual"})
    predicted = pd.DataFrame({
        "Period": future_months,
        "Actual": np.nan,
        "Type": "Forecast",
        "Forecast": np.maximum(forecast, 0),
        "Lower": np.maximum(forecast - 1.96 * residual_std, 0),
        "Upper": forecast + 1.96 * residual_std,
    })
    fitted_frame = pd.DataFrame({"Period": monthly.index, "Actual": y, "Type": "Actual", "Forecast": fitted})
    return pd.concat([fitted_frame, predicted], ignore_index=True), {
        "method": "Linear trend fitted with ordinary least squares",
        "residual_standard_deviation": residual_std,
        "limitations": "A simple trend model; it ignores seasonality, promotions, inventory, and external shocks.",
    }
