"""Orchestrate the ecommerce sales extract, transform, and load workflow."""

from extract import extract_data
from load import load_data
from transform import transform_data


def main() -> None:
    """Run the complete ETL pipeline and report its progress."""
    print("=" * 30)
    print("STARTING ETL PIPELINE")
    print("=" * 30)

    try:
        # Step 1: Read the raw ecommerce sales dataset.
        extract_data()
        print("Step 1: Extract Completed")

        # Step 2: Clean the extracted data and save the cleaned CSV file.
        transform_data()
        print("Step 2: Transform Completed")

        # Step 3: Load the cleaned CSV file into the warehouse directory.
        load_data()
        print("Step 3: Load Completed")

    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"ETL pipeline failed: {error}")
        return
    except Exception as error:
        print(f"Unexpected ETL pipeline error: {error}")
        return

    print("=" * 30)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 30)


if __name__ == "__main__":
    main()
