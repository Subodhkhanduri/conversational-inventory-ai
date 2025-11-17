# inventory_chatbot/analytics/forecasting.py

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import timedelta


class ForecastingTool:

    def generate_forecast(self, df, item=None, store=None, periods=10):
        """
        Generates a simple forecast using average daily sales.

        df       : the full uploaded dataframe
        item     : optional -> filter by item ID
        store    : optional -> filter by store ID
        periods  : number of days to forecast
        """

        # ---------------------------
        # FILTER BY STORE + ITEM
        # ---------------------------
        if store is not None:
            df = df[df["store"] == store]

        if item is not None:
            df = df[df["item"] == item]

        if df.empty:
            raise ValueError("No data available for the selected item/store.")

        # ---------------------------
        # PREPARE FORECAST INPUT
        # ---------------------------
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        # Use Daily_Sales as demand proxy
        if "Daily_Sales" not in df.columns:
            raise ValueError("Daily_Sales column missing — required for forecasting.")

        # Average demand
        avg_sales = df["Daily_Sales"].mean()

        # Last date in dataset
        last_date = df["Date"].max()

        # ---------------------------
        # GENERATE FUTURE FORECAST
        # ---------------------------
        future_dates = [last_date + timedelta(days=i + 1) for i in range(periods)]
        forecast_values = [round(avg_sales, 2)] * periods

        forecast_df = pd.DataFrame({
            "Date": future_dates,
            "Forecasted_Demand": forecast_values
        })

        # ---------------------------
        # PLOT FORECAST
        # ---------------------------
        fig, ax = plt.subplots(figsize=(8, 4))

        # Historical
        ax.plot(df["Date"], df["Daily_Sales"], label="Historical Sales")

        # Forecast
        ax.plot(
            forecast_df["Date"],
            forecast_df["Forecasted_Demand"],
            label="Forecast",
            linestyle="--",
            marker="o"
        )

        ax.set_title(f"Demand Forecast (Item {item}, Store {store})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sales")
        ax.legend()

        # Save to PNG bytes
        img_bytes = BytesIO()
        plt.tight_layout()
        plt.savefig(img_bytes, format="png")
        plt.close()
        img_bytes.seek(0)

        # Return bytes + forecasted values
        return img_bytes.read(), forecast_df.to_dict(orient="records")
