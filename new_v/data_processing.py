import pandas as pd
from datetime import datetime


def process_data(data: pd.DataFrame) -> pd.DataFrame:
    # Find the header row and clean the data
    header_row = data[data.eq('תאריך').any(axis=1)].index[0]
    data_cleaned = data.iloc[header_row:].reset_index(drop=True)
    data_cleaned.columns = data_cleaned.iloc[0]
    data_cleaned = data_cleaned[1:].reset_index(drop=True)

    # Convert date column to datetime
    data_cleaned['תאריך'] = pd.to_datetime(data_cleaned['תאריך'])

    return data_cleaned


def filter_data_by_date(data: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    return data[(data['תאריך'].dt.date >= start_date) & (data['תאריך'].dt.date <= end_date)]
