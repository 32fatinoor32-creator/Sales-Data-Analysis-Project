"""Streamlit dashboard for the final ecommerce sales dataset."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Configure the page before rendering any dashboard elements.
st.set_page_config(
    page_title="Ecommerce Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "warehouse"
    / "final_ecommerce_sales.csv"
)
FILTER_COLUMNS = ("Region", "Category", "Customer_Segment", "Payment_Method")
CHART_TEMPLATE = "plotly_white"


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and return the final ecommerce sales dataset.

    Raises:
        FileNotFoundError: If the warehouse CSV file does not exist.
    """
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(f"Dataset not found: '{DATASET_PATH}'.")

    return pd.read_csv(DATASET_PATH)


def filter_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create sidebar filters and return the matching dataset rows.

    An empty multiselect leaves that dimension unfiltered.

    Args:
        dataframe: Complete ecommerce sales dataset.

    Returns:
        A DataFrame filtered by the active sidebar selections.
    """
    missing_columns = set(FILTER_COLUMNS).difference(dataframe.columns)
    if missing_columns:
        raise KeyError(f"Filter column(s) missing: {sorted(missing_columns)}")

    st.sidebar.header("Filters")
    selected_regions = st.sidebar.multiselect(
        "Region", options=sorted(dataframe["Region"].dropna().unique())
    )
    selected_categories = st.sidebar.multiselect(
        "Category", options=sorted(dataframe["Category"].dropna().unique())
    )
    selected_segments = st.sidebar.multiselect(
        "Customer Segment",
        options=sorted(dataframe["Customer_Segment"].dropna().unique()),
    )
    selected_payment_methods = st.sidebar.multiselect(
        "Payment Method",
        options=sorted(dataframe["Payment_Method"].dropna().unique()),
    )

    selections = {
        "Region": selected_regions,
        "Category": selected_categories,
        "Customer_Segment": selected_segments,
        "Payment_Method": selected_payment_methods,
    }
    filtered_dataframe = dataframe.copy()

    # Apply only filters with selections so empty multiselects retain all rows.
    for column, selected_values in selections.items():
        if selected_values:
            filtered_dataframe = filtered_dataframe[
                filtered_dataframe[column].isin(selected_values)
            ]

    return filtered_dataframe


def display_charts(dataframe: pd.DataFrame) -> None:
    """Render interactive Plotly charts using the currently filtered records.

    Args:
        dataframe: Ecommerce sales data after sidebar filters are applied.
    """
    required_columns = {
        "Order_Date",
        "Revenue",
        "Profit",
        "Category",
        "Region",
        "Customer_Segment",
        "Product_Name",
        "Order_Status",
    }
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        raise KeyError(f"Chart column(s) missing: {sorted(missing_columns)}")

    st.subheader("Sales Insights")
    if dataframe.empty:
        st.warning("No records match the selected filters.")
        return

    chart_data = dataframe.copy()
    chart_data["Revenue"] = pd.to_numeric(chart_data["Revenue"], errors="coerce")
    chart_data["Profit"] = pd.to_numeric(chart_data["Profit"], errors="coerce")
    chart_data["Order_Date"] = pd.to_datetime(chart_data["Order_Date"], errors="coerce")

    revenue_by_category = (
        chart_data.groupby("Category", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    revenue_by_region = (
        chart_data.groupby("Region", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    monthly_revenue = (
        chart_data.dropna(subset=["Order_Date"])
        .assign(Month=lambda frame: frame["Order_Date"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month", as_index=False)["Revenue"]
        .sum()
        .sort_values("Month")
    )
    profit_by_segment = (
        chart_data.groupby("Customer_Segment", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit", ascending=False)
    )
    top_products = (
        chart_data.groupby("Product_Name", as_index=False)["Revenue"]
        .sum()
        .nlargest(10, "Revenue")
        .sort_values("Revenue")
    )
    order_statuses = (
        chart_data["Order_Status"].value_counts().rename_axis("Order_Status")
        .reset_index(name="Orders")
    )

    # Two chart columns keep the dashboard compact and easy to scan.
    left_column, right_column = st.columns(2)
    with left_column:
        category_chart = px.bar(
            revenue_by_category,
            x="Category",
            y="Revenue",
            title="Revenue by Category",
            template=CHART_TEMPLATE,
        )
        category_chart.update_layout(height=400)
        st.plotly_chart(category_chart, use_container_width=True)
    with right_column:
        region_chart = px.bar(
            revenue_by_region,
            x="Region",
            y="Revenue",
            title="Revenue by Region",
            template=CHART_TEMPLATE,
        )
        region_chart.update_layout(height=400)
        st.plotly_chart(region_chart, use_container_width=True)

    left_column, right_column = st.columns(2)
    with left_column:
        monthly_chart = px.line(
            monthly_revenue,
            x="Month",
            y="Revenue",
            title="Monthly Revenue Trend",
            markers=True,
            template=CHART_TEMPLATE,
        )
        monthly_chart.update_layout(height=400)
        st.plotly_chart(monthly_chart, use_container_width=True)
    with right_column:
        segment_chart = px.pie(
            profit_by_segment,
            names="Customer_Segment",
            values="Profit",
            title="Profit by Customer Segment",
            template=CHART_TEMPLATE,
        )
        segment_chart.update_layout(height=400)
        st.plotly_chart(segment_chart, use_container_width=True)

    left_column, right_column = st.columns(2)
    with left_column:
        products_chart = px.bar(
            top_products,
            x="Revenue",
            y="Product_Name",
            orientation="h",
            title="Top 10 Products by Revenue",
            template=CHART_TEMPLATE,
        )
        products_chart.update_layout(height=400)
        st.plotly_chart(products_chart, use_container_width=True)
    with right_column:
        status_chart = px.pie(
            order_statuses,
            names="Order_Status",
            values="Orders",
            title="Order Status Distribution",
            hole=0.5,
            template=CHART_TEMPLATE,
        )
        status_chart.update_layout(height=400)
        st.plotly_chart(status_chart, use_container_width=True)


def display_dashboard(dataframe: pd.DataFrame) -> None:
    """Render dashboard KPIs and an interactive preview of the dataset.

    Args:
        dataframe: Final ecommerce sales data to display.
    """
    required_columns = {"Revenue", "Profit", "Profit_Margin_%", "Order_ID"}
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        raise KeyError(f"Required column(s) missing: {sorted(missing_columns)}")

    revenue = pd.to_numeric(dataframe["Revenue"], errors="coerce").sum()
    profit = pd.to_numeric(dataframe["Profit"], errors="coerce").sum()
    average_profit_margin = pd.to_numeric(
        dataframe["Profit_Margin_%"], errors="coerce"
    ).mean()
    total_orders = dataframe["Order_ID"].nunique()

    st.title("Ecommerce Sales Dashboard")
    st.subheader("Dataset Overview")

    dataset_shape, total_revenue, total_profit, total_order_count, avg_margin = st.columns(5)
    dataset_shape.metric("Dataset Shape", f"{dataframe.shape[0]:,} × {dataframe.shape[1]}")
    total_revenue.metric("Total Revenue", f"${revenue:,.2f}")
    total_profit.metric("Total Profit", f"${profit:,.2f}")
    total_order_count.metric("Total Orders", f"{total_orders:,}")
    avg_margin.metric(
        "Average Profit Margin",
        f"{average_profit_margin:.2f}%" if pd.notna(average_profit_margin) else "N/A",
    )

    display_charts(dataframe)

    st.subheader("First 10 Records")
    st.dataframe(dataframe.head(10), use_container_width=True)


def main() -> None:
    """Load the dataset and render the dashboard with error handling."""
    try:
        dataframe = load_data()
        filtered_dataframe = filter_data(dataframe)
        display_dashboard(filtered_dataframe)
    except (FileNotFoundError, KeyError, ValueError, pd.errors.ParserError) as error:
        st.error(f"Unable to load the dashboard: {error}")


if __name__ == "__main__":
    main()
