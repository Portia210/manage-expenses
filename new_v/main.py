# main.py

import pandas as pd
from data_processing import process_data
from report_generation import generate_reports
from utils import get_date_range_input


def main():
    # Load and process data
    raw_data = pd.read_excel('../bank.xlsx', header=None)
    processed_data = process_data(raw_data)

    # Get date range from user
    start_date, end_date = get_date_range_input()

    # Generate reports
    generate_reports(processed_data, start_date, end_date)

    print("All reports have been generated successfully.")


if __name__ == "__main__":
    main()

# data_processing.py



# report_generation.py


# calculations.py



# file_operations.py



# utils.py

