"""Generate visual EDA charts for the final ecommerce sales dataset."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "warehouse" / "final_ecommerce_sales.csv"
CHARTS_PATH = PROJECT_ROOT / "reports" / "charts"
CHART_DPI = 300


def save_chart(figure: plt.Figure, filename: str) -> None:
    """Save a figure at high resolution, close it, and report its path.

    Args:
        figure: The matplotlib figure to save.
        filename: Name of the PNG file in the charts directory.
    """
    output_path = CHARTS_PATH / filename
    figure.tight_layout()
    figure.savefig(output_path, dpi=CHART_DPI, bbox_inches="tight")
    plt.close(figure)
    print(f"Saved chart: {filename}")


def create_visualizations() -> None:
    """Load sales data and generate all required visualization PNG files.

    Raises:
        FileNotFoundError: If the final warehouse dataset is unavailable.
        KeyError: If a required dataset column is missing.
    """
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(f"Warehouse dataset not found: '{DATASET_PATH}'.")

    dataframe = pd.read_csv(DATASET_PATH)
    required_columns = {
        "Order_Date",
        "Revenue",
        "Category",
        "Profit",
        "Region",
        "Customer_Segment",
        "Payment_Method",
        "Shipping_Method",
        "Order_Status",
        "Product_Name",
    }
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        raise KeyError(f"Required column(s) missing: {sorted(missing_columns)}")

    # Prepare date and measure fields before creating grouped visualizations.
    dataframe["Order_Date"] = pd.to_datetime(dataframe["Order_Date"], errors="coerce")
    dataframe["Revenue"] = pd.to_numeric(dataframe["Revenue"], errors="coerce")
    dataframe["Profit"] = pd.to_numeric(dataframe["Profit"], errors="coerce")
    CHARTS_PATH.mkdir(parents=True, exist_ok=True)

    monthly_data = dataframe.dropna(subset=["Order_Date"]).copy()
    monthly_data["Order_Month"] = monthly_data["Order_Date"].dt.to_period("M")
    monthly_revenue = monthly_data.groupby("Order_Month")["Revenue"].sum()
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.plot(monthly_revenue.index.astype(str), monthly_revenue.values, marker="o")
    axis.set_title("Monthly Revenue Trend")
    axis.set_xlabel("Month")
    axis.set_ylabel("Revenue")
    axis.tick_params(axis="x", rotation=45)
    axis.grid(True, alpha=0.3)
    save_chart(figure, "monthly_revenue_trend.png")

    revenue_by_category = dataframe.groupby("Category")["Revenue"].sum().sort_values()
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.bar(revenue_by_category.index, revenue_by_category.values)
    axis.set_title("Revenue by Category")
    axis.set_xlabel("Category")
    axis.set_ylabel("Revenue")
    axis.tick_params(axis="x", rotation=45)
    save_chart(figure, "revenue_by_category.png")

    profit_by_region = dataframe.groupby("Region")["Profit"].sum().sort_values()
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.bar(profit_by_region.index, profit_by_region.values)
    axis.set_title("Profit by Region")
    axis.set_xlabel("Region")
    axis.set_ylabel("Profit")
    axis.tick_params(axis="x", rotation=45)
    save_chart(figure, "profit_by_region.png")

    customer_segments = dataframe["Customer_Segment"].value_counts()
    figure, axis = plt.subplots(figsize=(8, 8))
    axis.pie(customer_segments.values, labels=customer_segments.index, autopct="%1.1f%%")
    axis.set_title("Customer Segment Distribution")
    axis.set_xlabel("Customer Segment")
    axis.set_ylabel("Share of Customers")
    save_chart(figure, "customer_segment_distribution.png")

    payment_methods = dataframe["Payment_Method"].value_counts()
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.bar(payment_methods.index, payment_methods.values)
    axis.set_title("Payment Method Distribution")
    axis.set_xlabel("Payment Method")
    axis.set_ylabel("Number of Orders")
    axis.tick_params(axis="x", rotation=45)
    save_chart(figure, "payment_method_distribution.png")

    shipping_methods = dataframe["Shipping_Method"].value_counts()
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.bar(shipping_methods.index, shipping_methods.values)
    axis.set_title("Shipping Method Distribution")
    axis.set_xlabel("Shipping Method")
    axis.set_ylabel("Number of Orders")
    axis.tick_params(axis="x", rotation=45)
    save_chart(figure, "shipping_method_distribution.png")

    order_statuses = dataframe["Order_Status"].value_counts()
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.bar(order_statuses.index, order_statuses.values)
    axis.set_title("Order Status Distribution")
    axis.set_xlabel("Order Status")
    axis.set_ylabel("Number of Orders")
    axis.tick_params(axis="x", rotation=45)
    save_chart(figure, "order_status_distribution.png")

    top_products = dataframe.groupby("Product_Name")["Revenue"].sum().nlargest(10).sort_values()
    figure, axis = plt.subplots(figsize=(10, 7))
    axis.barh(top_products.index, top_products.values)
    axis.set_title("Top 10 Products by Revenue")
    axis.set_xlabel("Revenue")
    axis.set_ylabel("Product Name")
    save_chart(figure, "top_10_products_by_revenue.png")

    figure, axis = plt.subplots(figsize=(10, 6))
    axis.hist(dataframe["Profit"].dropna(), bins=30, edgecolor="black")
    axis.set_title("Profit Distribution")
    axis.set_xlabel("Profit")
    axis.set_ylabel("Frequency")
    save_chart(figure, "profit_distribution.png")

    numeric_data = dataframe.select_dtypes(include="number")
    correlation = numeric_data.corr()
    figure, axis = plt.subplots(figsize=(12, 10))
    image = axis.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
    axis.set_title("Correlation Heatmap (Numeric Columns)")
    axis.set_xlabel("Numeric Columns")
    axis.set_ylabel("Numeric Columns")
    axis.set_xticks(range(len(correlation.columns)), correlation.columns, rotation=45, ha="right")
    axis.set_yticks(range(len(correlation.columns)), correlation.columns)
    figure.colorbar(image, ax=axis, label="Correlation")
    save_chart(figure, "correlation_heatmap.png")


def main() -> None:
    """Generate charts and display an understandable error if processing fails."""
    try:
        create_visualizations()
    except (FileNotFoundError, KeyError, OSError, ValueError, pd.errors.ParserError) as error:
        print(f"Unable to generate visualizations: {error}")


if __name__ == "__main__":
    main()
