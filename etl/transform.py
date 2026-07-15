"""Clean the extracted ecommerce sales dataset."""

from pathlib import Path

import pandas as pd

from extract import extract_data


# Numeric fields expected in the ecommerce sales dataset.
NUMERIC_COLUMNS = [
    "Year",
    "Month",
    "Unit_Price",
    "Quantity",
    "Discount",
    "Revenue",
    "Cost",
    "Profit",
    "Profit_Margin_%",
    "Shipping_Cost",
    "Shipping_Days",
]

# Store the cleaned output under the project's data directory.
OUTPUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "cleaned"
    / "cleaned_ecommerce_sales.csv"
)


def transform_data() -> pd.DataFrame:
    """Load, clean, save, and return the ecommerce sales dataset.

    Returns:
        A cleaned DataFrame containing ecommerce sales records.
    """
    dataframe = extract_data()

    print("\nDataset information:")
    dataframe.info()
    print("\nSummary statistics:")
    print(dataframe.describe())

    missing_values = dataframe.isna().sum()
    print("\nMissing values by column:")
    print(missing_values)
    if missing_values.any():
        print("Cleaning action: Missing values were identified; no values were removed.")
    else:
        print("Cleaning action: No missing values found.")

    duplicate_count = dataframe.duplicated().sum()
    print(f"\nDuplicate rows found: {duplicate_count}")
    if duplicate_count:
        dataframe = dataframe.drop_duplicates().copy()
        print(f"Cleaning action: Removed {duplicate_count} duplicate row(s).")
    else:
        print("Cleaning action: No duplicate rows required removal.")

    dataframe["Order_Date"] = pd.to_datetime(
        dataframe["Order_Date"], errors="coerce"
    )
    invalid_date_count = dataframe["Order_Date"].isna().sum()
    print(
        "Cleaning action: Converted 'Order_Date' to datetime "
        f"({invalid_date_count} invalid or missing date(s) converted to NaT)."
    )

    available_numeric_columns = [
        column for column in NUMERIC_COLUMNS if column in dataframe.columns
    ]
    dataframe[available_numeric_columns] = dataframe[available_numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    print(
        "Cleaning action: Converted numeric columns to numeric data types: "
        f"{available_numeric_columns}."
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(OUTPUT_PATH, index=False)
    print(f"Cleaning action: Saved cleaned dataset to '{OUTPUT_PATH}'.")

    return dataframe


if __name__ == "__main__":
    transform_data()
