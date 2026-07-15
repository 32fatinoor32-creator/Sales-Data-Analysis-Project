"""Create an exploratory data analysis summary for warehouse sales data."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd


# Use paths relative to the project root so the script works from any directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "warehouse" / "final_ecommerce_sales.csv"
REPORT_PATH = PROJECT_ROOT / "reports" / "eda_summary.txt"


def create_eda_summary() -> str:
    """Load warehouse data, print EDA findings, and save them as a text report.

    Returns:
        The complete EDA report content.

    Raises:
        FileNotFoundError: If the warehouse dataset is unavailable.
        OSError: If the report cannot be written.
    """
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(f"Warehouse dataset not found: '{DATASET_PATH}'.")

    dataframe = pd.read_csv(DATASET_PATH)
    report_sections: list[str] = []

    # Capture DataFrame.info() because it normally writes directly to stdout.
    info_buffer = StringIO()
    dataframe.info(buf=info_buffer)

    report_sections.extend(
        [
            "DATASET SHAPE",
            str(dataframe.shape),
            "\nDATASET INFO",
            info_buffer.getvalue().rstrip(),
            "\nDATA TYPES",
            dataframe.dtypes.to_string(),
            "\nMISSING VALUES",
            dataframe.isna().sum().to_string(),
            "\nDUPLICATE ROWS",
            str(dataframe.duplicated().sum()),
            "\nSUMMARY STATISTICS",
            dataframe.describe(include="all").to_string(),
            "\nUNIQUE VALUES FOR CATEGORICAL COLUMNS",
        ]
    )

    categorical_columns = dataframe.select_dtypes(include=["object", "category"]).columns
    if categorical_columns.empty:
        report_sections.append("No categorical columns found.")
    else:
        for column in categorical_columns:
            unique_values = dataframe[column].drop_duplicates().tolist()
            report_sections.append(f"{column}: {unique_values}")

    report_content = "\n".join(report_sections)
    print(report_content)

    # Ensure the destination folder exists before saving the EDA output.
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_content, encoding="utf-8")
    print(f"\nEDA summary saved to: {REPORT_PATH}")

    return report_content


def main() -> None:
    """Run EDA summary generation and display any processing error."""
    try:
        create_eda_summary()
    except (FileNotFoundError, OSError, pd.errors.ParserError) as error:
        print(f"Unable to generate EDA summary: {error}")


if __name__ == "__main__":
    main()
