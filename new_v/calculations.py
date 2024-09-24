import pandas as pd
import re
from typing import Dict


def earning_expenses(data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    earnings_data = data[data['זכות'].notna()].copy()
    expenses_data = data[data['חובה'].notna()].copy()

    l_earnings_grouped = group_by_operation_and_details(earnings_data, 'זכות')
    l_expenses_grouped = group_by_operation_and_details(expenses_data, 'חובה')
    s_earnings_grouped = group_by_operation(earnings_data, 'זכות')
    s_expenses_grouped = group_by_operation(expenses_data, 'חובה')

    for df in [l_earnings_grouped, l_expenses_grouped, s_earnings_grouped, s_expenses_grouped]:
        df = add_total_row(df, 'זכות' if 'זכות' in df.columns else 'חובה')
        clean_dataframe(df)

    return {
        "s_earnings": s_earnings_grouped,
        "s_expenses": s_expenses_grouped,
        "l_earnings": l_earnings_grouped,
        "l_expenses": l_expenses_grouped
    }


def group_by_operation_and_details(data: pd.DataFrame, amount_col: str) -> pd.DataFrame:
    data['פרטים'] = data['פרטים'].fillna('(ללא פרטים)')
    grouped = data.groupby(['הפעולה', 'פרטים']).agg({
        'תאריך': format_date_range,
        amount_col: ['sum', 'count']
    }).reset_index()
    grouped.columns = ['הפעולה', 'פרטים', 'תאריך', amount_col, 'מספר טרנזקציות']
    grouped['מספר טרנזקציות'] = grouped['מספר טרנזקציות'].astype(int)
    return grouped[['הפעולה', 'פרטים', 'תאריך', 'מספר טרנזקציות', amount_col]]


def group_by_operation(data: pd.DataFrame, amount_col: str) -> pd.DataFrame:
    return data.groupby('הפעולה').agg({
        amount_col: 'sum',
        'פרטים': lambda x: ', '.join(filter(None, set(clean_text(i) for i in x)))
    }).reset_index()


def add_total_row(df: pd.DataFrame, sum_column: str) -> pd.DataFrame:
    total = round_numbers(df[sum_column].sum())
    total_transactions = df['מספר טרנזקציות'].sum() if 'מספר טרנזקציות' in df.columns else ''
    total_data = {col: ['סך הכל' if col == df.columns[0] else
                        total if col == sum_column else
                        total_transactions if col == 'מספר טרנזקציות' else '']
                  for col in df.columns}
    total_row = pd.DataFrame(total_data, index=[0], columns=df.columns, dtype=object)
    return pd.concat([df, total_row], ignore_index=True)


def clean_dataframe(df: pd.DataFrame):
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].apply(round_numbers)
        elif col == 'פרטים':
            df[col] = df[col].apply(lambda x: clean_text(x) if x != '(ללא פרטים)' else x)


def format_date_range(dates):
    return dates.iloc[0].strftime('%d/%m/%y') if len(
        dates) == 1 else f"{dates.min().strftime('%d/%m/%y')} - {dates.max().strftime('%d/%m/%y')}"


def round_numbers(x):
    return round(x, 1) if isinstance(x, float) else x


def clean_text(text):
    if pd.isna(text):
        return ''
    if isinstance(text, str):
        text = ' '.join(text.split())
        text = re.sub(r'\s+([,.])', r'\1', text)
    return text
