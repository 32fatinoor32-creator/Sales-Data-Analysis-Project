"""Extract the raw ecommerce sales dataset into a pandas DataFrame."""

from pathlib import Path

import pandas as pd


# Resolve the dataset location from the project root so this module can be run
# from any working directory.
DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "ecommerce_sales_dataset.csv"
)


def extract_data() -> pd.DataFrame:
    """Load the raw ecommerce sales CSV file and print a brief overview.

    Returns:
        A DataFrame containing the raw ecommerce sales data.

    Raises:
        FileNotFoundError: If the expected CSV file is not present.
    """
    if not DATASET_PATH.is_file():
        message = f"Error: Dataset file not found at '{DATASET_PATH}'."
        print(message)
        raise FileNotFoundError(message)

    dataframe = pd.read_csv(DATASET_PATH)

    print(f"Dataset shape: {dataframe.shape}")
    print(f"Number of columns: {dataframe.shape[1]}")
    print(f"Column names: {dataframe.columns.tolist()}")
    print("First five rows:")
    print(dataframe.head())

    return dataframe


if __name__ == "__main__":
    extract_data()
