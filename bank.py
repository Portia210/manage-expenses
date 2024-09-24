import pandas as pd
import os
from datetime import datetime
import re
from typing import Dict


# from combine_dfs import combine_dfs_with_separation


def round_numbers(x):
    if isinstance(x, (int, float)):
        return round(x, 1) if isinstance(x, float) else x
    return x


def clean_text(text):
    if pd.isna(text):
        return ''
    if isinstance(text, str):
        # Remove extra spaces
        text = ' '.join(text.split())
        # Remove spaces before punctuation
        text = re.sub(r'\s+([,.])', r'\1', text)
    return text


def add_total_row(dataframe, sum_column):
    total = round_numbers(dataframe[sum_column].sum())
    total_transactions = dataframe['מספר טרנזקציות'].sum() if 'מספר טרנזקציות' in dataframe.columns else ''

    total_data = {
        column: ['סך הכל' if column == dataframe.columns[0] else
                 total if column == sum_column else
                 total_transactions if column == 'מספר טרנזקציות' else
                 '']
        for column in dataframe.columns
    }

    total_row = pd.DataFrame(
        data=total_data,
        index=[0],
        columns=dataframe.columns,
        dtype=object
    )

    # Ensure the total_row has the same dtypes as the original DataFrame
    for column in dataframe.columns:
        if column in ['מספר טרנזקציות', sum_column]:
            total_row[column] = total_row[column].astype(dataframe[column].dtype)
        else:
            total_row[column] = total_row[column].astype(str)

    return pd.concat([dataframe, total_row], ignore_index=True)


def earning_expenses(initial_data) -> Dict[str, pd.DataFrame]:
    earnings_data = initial_data[initial_data['זכות'].notna()].copy()
    expenses_data = initial_data[initial_data['חובה'].notna()].copy()

    # Function to format date range
    def format_date_range(dates):
        if len(dates) == 1:
            return dates.iloc[0].strftime('%d/%m/%y')
        else:
            return f"{dates.min().strftime('%d/%m/%y')} - {dates.max().strftime('%d/%m/%y')}"

    # Function to group by 'הפעולה' and 'פרטים' (long version)
    def group_by_operation_and_details(data, amount_col):
        data['פרטים'] = data['פרטים'].fillna('(ללא פרטים)')

        grouped = data.groupby(['הפעולה', 'פרטים']).agg({
            'תאריך': format_date_range,
            amount_col: ['sum', 'count']
        }).reset_index()

        grouped.columns = ['הפעולה', 'פרטים', 'תאריך', amount_col, 'מספר טרנזקציות']
        grouped['מספר טרנזקציות'] = grouped['מספר טרנזקציות'].astype(int)

        column_order = ['הפעולה', 'פרטים', 'תאריך', 'מספר טרנזקציות', amount_col]
        return grouped[column_order]

    # Function to group by 'הפעולה' only (short version)
    def group_by_operation(data, amount_col):
        grouped = data.groupby('הפעולה').agg({
            amount_col: 'sum',
            'פרטים': lambda x: ', '.join(filter(None, set(clean_text(i) for i in x)))
        }).reset_index()

        return grouped

    # Group earnings (long version)
    l_earnings_grouped = group_by_operation_and_details(earnings_data, 'זכות')

    # Group expenses (long version)
    l_expenses_grouped = group_by_operation_and_details(expenses_data, 'חובה')

    # Group earnings (short version)
    s_earnings_grouped = group_by_operation(earnings_data, 'זכות')

    # Group expenses (short version)
    s_expenses_grouped = group_by_operation(expenses_data, 'חובה')

    # Add sum rows
    for df in [l_earnings_grouped, l_expenses_grouped, s_earnings_grouped, s_expenses_grouped]:
        df = add_total_row(df, 'זכות' if 'זכות' in df.columns else 'חובה')

    # Round numbers and clean text
    for data in [l_earnings_grouped, l_expenses_grouped, s_earnings_grouped, s_expenses_grouped]:
        for col in data.columns:
            if data[col].dtype in ['float64', 'int64']:
                data[col] = data[col].apply(round_numbers)
            elif col == 'פרטים':
                data[col] = data[col].apply(lambda x: clean_text(x) if x != '(ללא פרטים)' else x)

    return {"s_earnings": s_earnings_grouped,
            "s_expenses": s_expenses_grouped,
            "l_earnings": l_earnings_grouped,
            "l_expenses": l_expenses_grouped}


def get_date_input(prompt):
    while True:
        date_str = input(prompt)
        if date_str == "":
            return None
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            print("Invalid date format. Please use DD/MM/YYYY or press Enter to skip.")


# Read the Excel file
data = pd.read_excel('bank.xlsx', header=None)

# Find the first row that contains 'תאריך' (assuming this is the header row)
header_row = data[data.eq('תאריך').any(axis=1)].index[0]

# Select the data from the header row onwards
data_cleaned = data.iloc[header_row:].reset_index(drop=True)

# Set the first row as the header
data_cleaned.columns = data_cleaned.iloc[0]
data_cleaned = data_cleaned[1:]

# Reset the index
data_cleaned.reset_index(drop=True, inplace=True)
# Convert the 'תאריך' column to datetime
data_cleaned['תאריך'] = pd.to_datetime(data_cleaned['תאריך'])

# Get user input for date range
start_date = get_date_input("Enter start date (DD/MM/YYYY) or press Enter for all dates: ")
end_date = get_date_input("Enter end date (DD/MM/YYYY) or press Enter for all dates: ")

# If no dates are provided, use the earliest and latest dates from the data
if not start_date:
    start_date = data_cleaned['תאריך'].min().date()
if not end_date:
    end_date = data_cleaned['תאריך'].max().date()

# Filter the dataframe based on user input or data range
data_cleaned = data_cleaned[(data_cleaned['תאריך'].dt.date >= start_date) & (data_cleaned['תאריך'].dt.date <= end_date)]

# Create a folder to store the output files
output_folder = 'all_reports'
os.makedirs(output_folder, exist_ok=True)

# Calculate for all dates
all_dates_dfs = earning_expenses(data_cleaned)
date_range = f"{start_date.strftime('%d-%m-%Y')}_to_{end_date.strftime('%d-%m-%Y')}"

all_dates_dfs["l_earnings"].to_csv(os.path.join(output_folder, f'earnings_{date_range}.csv'), index=False,
                                   encoding='utf-8-sig')
all_dates_dfs["l_expenses"].to_csv(os.path.join(output_folder, f'expenses_{date_range}.csv'), index=False,
                                   encoding='utf-8-sig')

# Calculate for each year
for year in range(data_cleaned['תאריך'].dt.year.min(), data_cleaned['תאריך'].dt.year.max() + 1):
    year_data = data_cleaned[(data_cleaned['תאריך'].dt.year == year)]
    if not year_data.empty:
        year_dfs = earning_expenses(year_data)
        year_folder = os.path.join(output_folder, str(year))
        os.makedirs(year_folder, exist_ok=True)
        year_dfs["l_earnings"].to_csv(os.path.join(year_folder, f'earnings_{year}.csv'), index=False,
                                      encoding='utf-8-sig')
        year_dfs["l_expenses"].to_csv(os.path.join(year_folder, f'expenses_{year}.csv'), index=False,
                                      encoding='utf-8-sig')

# Calculate for each month
grouped = data_cleaned.groupby(data_cleaned['תאריך'].dt.to_period('M'))

for month, month_data in grouped:
    monthly_dfs = earning_expenses(month_data)

    # Create a subfolder for each month
    month_folder = os.path.join(output_folder, month.strftime('%Y-%m'))
    os.makedirs(month_folder, exist_ok=True)

    # Export the grouped DataFrames to CSV files
    monthly_dfs["l_earnings"].to_csv(os.path.join(month_folder, f'earnings_{month}.csv'), index=False,
                                     encoding='utf-8-sig')
    monthly_dfs["l_expenses"].to_csv(os.path.join(month_folder, f'expenses_{month}.csv'), index=False,
                                     encoding='utf-8-sig')

print("All files have been exported successfully.")
