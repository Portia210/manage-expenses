import pandas as pd
import os
from datetime import datetime
import re
from typing import Dict, List, Union, Optional
import logging
from pathlib import Path
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DATE_FORMAT = config['DEFAULT']['DATE_FORMAT']
INPUT_FILE = config['DEFAULT']['INPUT_FILE']
OUTPUT_FOLDER = config['DEFAULT']['OUTPUT_FOLDER']

def round_numbers(x: Union[int, float, str]) -> Union[int, float, str]:
    """Round float numbers to 1 decimal place."""
    if isinstance(x, float):
        return round(x, 1)
    return x

def clean_text(text: Optional[str]) -> str:
    """Clean and format text strings."""
    if pd.isna(text):
        return ''
    if isinstance(text, str):
        text = ' '.join(text.split())
        text = re.sub(r'\s+([,.])', r'\1', text)
    return text

def add_total_row(dataframe: pd.DataFrame, sum_column: str) -> pd.DataFrame:
    """Add a total row to the dataframe."""
    total = round_numbers(dataframe[sum_column].sum())
    total_transactions = dataframe['מספר טרנזקציות'].sum() if 'מספר טרנזקציות' in dataframe.columns else ''

    total_data = {
        column: ['סך הכל' if column == dataframe.columns[0] else
                 total if column == sum_column else
                 total_transactions if column == 'מספר טרנזקציות' else
                 '']
        for column in dataframe.columns
    }

    total_row = pd.DataFrame(total_data, index=[0], columns=dataframe.columns, dtype=object)

    for column in dataframe.columns:
        if column in ['מספר טרנזקציות', sum_column]:
            total_row[column] = total_row[column].astype(dataframe[column].dtype)
        else:
            total_row[column] = total_row[column].astype(str)

    return pd.concat([dataframe, total_row], ignore_index=True)

def format_date_range(dates: pd.Series) -> str:
    """Format a date range as a string."""
    if len(dates) == 1:
        return dates.iloc[0].strftime(DATE_FORMAT)
    return f"{dates.min().strftime(DATE_FORMAT)} - {dates.max().strftime(DATE_FORMAT)}"

def group_by_operation_and_details(data: pd.DataFrame, amount_col: str) -> pd.DataFrame:
    """Group data by operation and details (long version)."""
    data['פרטים'] = data['פרטים'].fillna('(ללא פרטים)')

    grouped = data.groupby(['הפעולה', 'פרטים']).agg({
        'תאריך': format_date_range,
        amount_col: ['sum', 'count']
    }).reset_index()

    grouped.columns = ['הפעולה', 'פרטים', 'תאריך', amount_col, 'מספר טרנזקציות']
    grouped['מספר טרנזקציות'] = grouped['מספר טרנזקציות'].astype(int)

    column_order = ['הפעולה', 'פרטים', 'תאריך', 'מספר טרנזקציות', amount_col]
    return grouped[column_order]

def group_by_operation(data: pd.DataFrame, amount_col: str) -> pd.DataFrame:
    """Group data by operation only (short version)."""
    return data.groupby('הפעולה').agg({
        amount_col: 'sum',
        'פרטים': lambda x: ', '.join(filter(None, set(clean_text(i) for i in x)))
    }).reset_index()

def earning_expenses(initial_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Process earnings and expenses data."""
    earnings_data = initial_data[initial_data['זכות'].notna()].copy()
    expenses_data = initial_data[initial_data['חובה'].notna()].copy()

    l_earnings_grouped = group_by_operation_and_details(earnings_data, 'זכות')
    l_expenses_grouped = group_by_operation_and_details(expenses_data, 'חובה')
    s_earnings_grouped = group_by_operation(earnings_data, 'זכות')
    s_expenses_grouped = group_by_operation(expenses_data, 'חובה')

    for df in [l_earnings_grouped, l_expenses_grouped, s_earnings_grouped, s_expenses_grouped]:
        df = add_total_row(df, 'זכות' if 'זכות' in df.columns else 'חובה')

    for data in [l_earnings_grouped, l_expenses_grouped, s_earnings_grouped, s_expenses_grouped]:
        for col in data.columns:
            if data[col].dtype in ['float64', 'int64']:
                data[col] = data[col].apply(round_numbers)
            elif col == 'פרטים':
                data[col] = data[col].apply(lambda x: clean_text(x) if x != '(ללא פרטים)' else x)

    return {
        "s_earnings": s_earnings_grouped,
        "s_expenses": s_expenses_grouped,
        "l_earnings": l_earnings_grouped,
        "l_expenses": l_expenses_grouped
    }

def get_date_input(prompt: str) -> Optional[datetime.date]:
    """Get date input from user."""
    while True:
        date_str = input(prompt)
        if date_str == "":
            return None
        try:
            return datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            logger.error(f"Invalid date format. Please use {DATE_FORMAT} or press Enter to skip.")

def export_dataframe(df: pd.DataFrame, filepath: Path) -> None:
    """Export DataFrame to CSV file."""
    try:
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Exported: {filepath}")
    except Exception as e:
        logger.error(f"Failed to export {filepath}: {str(e)}")

def main():
    try:
        # Read the Excel file
        data = pd.read_excel(INPUT_FILE, header=None)
    except FileNotFoundError:
        logger.error(f"Input file '{INPUT_FILE}' not found.")
        return
    except Exception as e:
        logger.error(f"Error reading input file: {str(e)}")
        return

    # Find the header row and clean the data
    header_row = data[data.eq('תאריך').any(axis=1)].index[0]
    data_cleaned = data.iloc[header_row:].reset_index(drop=True)
    data_cleaned.columns = data_cleaned.iloc[0]
    data_cleaned = data_cleaned[1:].reset_index(drop=True)

    # Convert the 'תאריך' column to datetime
    data_cleaned['תאריך'] = pd.to_datetime(data_cleaned['תאריך'])

    # Get user input for date range
    start_date = get_date_input(f"Enter start date ({DATE_FORMAT}) or press Enter for all dates: ")
    end_date = get_date_input(f"Enter end date ({DATE_FORMAT}) or press Enter for all dates: ")

    # If no dates are provided, use the earliest and latest dates from the data
    start_date = start_date or data_cleaned['תאריך'].min().date()
    end_date = end_date or data_cleaned['תאריך'].max().date()

    # Filter the dataframe based on date range
    data_cleaned = data_cleaned[(data_cleaned['תאריך'].dt.date >= start_date) & (data_cleaned['תאריך'].dt.date <= end_date)]

    # Create output folder
    output_folder = Path(OUTPUT_FOLDER)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Process and export data for all dates
    all_dates_dfs = earning_expenses(data_cleaned)
    date_range = f"{start_date.strftime('%d-%m-%Y')}_to_{end_date.strftime('%d-%m-%Y')}"

    export_dataframe(all_dates_dfs["l_earnings"], output_folder / f'earnings_{date_range}.csv')
    export_dataframe(all_dates_dfs["l_expenses"], output_folder / f'expenses_{date_range}.csv')

    # Process and export data for each year
    for year in range(data_cleaned['תאריך'].dt.year.min(), data_cleaned['תאריך'].dt.year.max() + 1):
        year_data = data_cleaned[data_cleaned['תאריך'].dt.year == year]
        if not year_data.empty:
            year_dfs = earning_expenses(year_data)
            year_folder = output_folder / str(year)
            year_folder.mkdir(exist_ok=True)
            export_dataframe(year_dfs["l_earnings"], year_folder / f'earnings_{year}.csv')
            export_dataframe(year_dfs["l_expenses"], year_folder / f'expenses_{year}.csv')

    # Process and export data for each month
    grouped = data_cleaned.groupby(data_cleaned['תאריך'].dt.to_period('M'))
    for month, month_data in grouped:
        monthly_dfs = earning_expenses(month_data)
        month_folder = output_folder / month.strftime('%Y-%m')
        month_folder.mkdir(exist_ok=True)
        export_dataframe(monthly_dfs["l_earnings"], month_folder / f'earnings_{month}.csv')
        export_dataframe(monthly_dfs["l_expenses"], month_folder / f'expenses_{month}.csv')

    logger.info("All files have been exported successfully.")

if __name__ == "__main__":
    main()