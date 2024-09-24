import pandas as pd
from datetime import datetime
import os
from typing import Dict
from calculations import earning_expenses
from file_operations import export_to_csv


def generate_reports(data: pd.DataFrame, start_date: datetime, end_date: datetime):
    output_folder = 'all_reports'
    os.makedirs(output_folder, exist_ok=True)

    # Generate overall report
    generate_overall_report(data, output_folder, start_date, end_date)

    # Generate yearly reports
    generate_yearly_reports(data, output_folder)

    # Generate monthly reports
    generate_monthly_reports(data, output_folder)


def generate_overall_report(data: pd.DataFrame, output_folder: str, start_date: datetime, end_date: datetime):
    dfs = earning_expenses(data)
    date_range = f"{start_date.strftime('%d-%m-%Y')}_to_{end_date.strftime('%d-%m-%Y')}"
    export_to_csv(dfs["l_earnings"], os.path.join(output_folder, f'earnings_{date_range}.csv'))
    export_to_csv(dfs["l_expenses"], os.path.join(output_folder, f'expenses_{date_range}.csv'))


def generate_yearly_reports(data: pd.DataFrame, output_folder: str):
    for year in range(data['תאריך'].dt.year.min(), data['תאריך'].dt.year.max() + 1):
        year_data = data[data['תאריך'].dt.year == year]
        if not year_data.empty:
            year_dfs = earning_expenses(year_data)
            year_folder = os.path.join(output_folder, str(year))
            os.makedirs(year_folder, exist_ok=True)
            export_to_csv(year_dfs["l_earnings"], os.path.join(year_folder, f'earnings_{year}.csv'))
            export_to_csv(year_dfs["l_expenses"], os.path.join(year_folder, f'expenses_{year}.csv'))


def generate_monthly_reports(data: pd.DataFrame, output_folder: str):
    grouped = data.groupby(data['תאריך'].dt.to_period('M'))
    for month, month_data in grouped:
        monthly_dfs = earning_expenses(month_data)
        month_folder = os.path.join(output_folder, month.strftime('%Y-%m'))
        os.makedirs(month_folder, exist_ok=True)
        export_to_csv(monthly_dfs["l_earnings"], os.path.join(month_folder, f'earnings_{month}.csv'))
        export_to_csv(monthly_dfs["l_expenses"], os.path.join(month_folder, f'expenses_{month}.csv'))

