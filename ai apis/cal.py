import pandas as pd
import os
from datetime import datetime
import re
from typing import Dict, List, Union, Optional
import logging
from pathlib import Path
import configparser
from claude_api import categorize_expenses
import asyncio



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



def clean_cell(x):
    if pd.isna(x):
        return x
    return re.sub(r'\s+', ' ', str(x).replace('\n', ' ')).strip()


def parse_date(date_input):
    if pd.isna(date_input):
        return pd.NaT

    if isinstance(date_input, pd.Timestamp):
        return date_input

    date_str = str(date_input).strip()

    formats = ['%d/%m/%y', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue

    print(f"Warning: Could not parse date '{date_str}'")
    return pd.NaT


def group_by_business(data) -> pd.DataFrame:
    # Group by 'שם בית עסק'
    grouped = data.groupby('שם בית עסק').agg({
        'תאריך עסקה': lambda x: f"{x.min().strftime('%Y-%m-%d')} - {x.max().strftime('%Y-%m-%d')}" if x.nunique() > 1 else x.iloc[0].strftime('%Y-%m-%d'),
        'סכום בש"ח': ['count', 'sum']
    }).reset_index()

    # Flatten column names
    grouped.columns = ['שם בית עסק', 'תאריכי ביצוע', 'מספר עסקאות', 'סכום כולל']

    # Ensure 'סכום כולל' is of type float
    grouped['סכום כולל'] = grouped['סכום כולל'].astype(float)

    # Round 'סכום כולל' to two decimal places
    grouped['סכום כולל'] = grouped['סכום כולל'].round(2)

    # Reorder columns
    grouped = grouped[['שם בית עסק', 'תאריכי ביצוע', 'מספר עסקאות', 'סכום כולל']]
    grouped = grouped.sort_values(by='סכום כולל', ascending=False)
    # Calculate the total sum of 'סכום כולל'
    total_sum = grouped['סכום כולל'].sum().round(1)

    # Append a row with the total sum and empty values for the other columns
    total_row = pd.DataFrame([['', '', '', total_sum]], columns=grouped.columns)
    grouped = pd.concat([grouped, total_row], ignore_index=True)

    return grouped



# Read the Excel file
data = pd.read_excel('cal.xlsx', header=None)

# Find the first row that contains 'תאריך' (assuming this is the header row)
header_row = data[data.astype(str).apply(lambda x: x.str.contains('תאריך', na=False)).any(axis=1)].index[0]

# Select the data from the header row onwards
data_cleaned = data.iloc[header_row:].reset_index(drop=True)

# Clean up column names: remove newlines and extra spaces
data_cleaned.columns = [clean_cell(col) for col in data_cleaned.iloc[0]]
data_cleaned = data_cleaned.iloc[1:].reset_index(drop=True)

# Clean up all cells: remove newlines and extra spaces
for col in data_cleaned.columns:
    data_cleaned[col] = data_cleaned[col].map(clean_cell)



# Convert the 'תאריך עסקה' column to datetime
if 'תאריך עסקה' in data_cleaned.columns:
    data_cleaned['תאריך עסקה'] = data_cleaned['תאריך עסקה'].map(parse_date)

# Convert the 'מועד חיוב' column to datetime
if 'מועד חיוב' in data_cleaned.columns:
    data_cleaned['מועד חיוב'] = data_cleaned['מועד חיוב'].map(parse_date)

# Remove rows after the last date
last_date_row = data_cleaned['תאריך עסקה'].last_valid_index()
if last_date_row is not None:
    data_cleaned = data_cleaned.iloc[:last_date_row + 1]

# Remove any remaining empty rows
data_cleaned = data_cleaned.dropna(how='all')
data_cleaned['סכום בש"ח'] = pd.to_numeric(data_cleaned['סכום בש"ח'], errors='coerce')

# Save to CSV
data_cleaned.to_csv("cal_cleaned.csv", index=False, encoding='utf-8-sig')

all_data_grouped=group_by_business(data_cleaned)
all_businesses= all_data_grouped['שם בית עסק'].to_list()
# print(all_businesses)
categorizations = categorize_expenses(all_businesses)
print(categorizations)

output_folder = 'all_reports'
os.makedirs(output_folder, exist_ok=True)

# Calculate for each month
grouped = data_cleaned.groupby(data_cleaned['תאריך עסקה'].dt.to_period('M'))

for month, month_data in grouped:
    monthly_credit_card = group_by_business(month_data)

    # Create a subfolder for each month
    month_folder = os.path.join(output_folder, month.strftime('%Y-%m'))
    os.makedirs(month_folder, exist_ok=True)

    # Export the grouped DataFrames to CSV files
    monthly_credit_card.to_csv(os.path.join(month_folder, f'cc_{month}.csv'), index=False,
                                     encoding='utf-8-sig')




