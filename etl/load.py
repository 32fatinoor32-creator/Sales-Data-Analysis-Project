"""Load the cleaned ecommerce sales dataset into the data warehouse."""

from pathlib import Path

import pandas as pd


# Resolve all paths from the project root to support any working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEANED_DATA_PATH = PROJECT_ROOT / "data" / "cleaned" / "cleaned_ecommerce_sales.csv"
WAREHOUSE_PATH = PROJECT_ROOT / "data" / "warehouse"
OUTPUT_PATH = WAREHOUSE_PATH / "final_ecommerce_sales.csv"


def load_data() -> pd.DataFrame:
    """Read, validate, and save cleaned ecommerce sales data for warehousing.

    Returns:
        The validated DataFrame written to the warehouse output file.

    Raises:
        FileNotFoundError: If the cleaned input CSV file does not exist.
        ValueError: If the cleaned dataset contains no rows.
    """
    if not CLEANED_DATA_PATH.is_file():
        message = f"Error: Cleaned dataset not found at '{CLEANED_DATA_PATH}'."
        print(message)
        raise FileNotFoundError(message)

    dataframe = pd.read_csv(CLEANED_DATA_PATH)

    if dataframe.empty:
        message = "Error: The cleaned dataset is empty; no data can be loaded."
        print(message)
        raise ValueError(message)

    print(f"Dataset shape: {dataframe.shape}")
    print(f"Total rows: {dataframe.shape[0]}")
    print(f"Total columns: {dataframe.shape[1]}")

    # Create the warehouse directory before writing the final dataset.
    WAREHOUSE_PATH.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(OUTPUT_PATH, index=False)

    print("Data loaded successfully.")
    print(f"Output file path: {OUTPUT_PATH}")
    print(f"Total records loaded: {len(dataframe)}")

    return dataframe


if __name__ == "__main__":
    load_data()
