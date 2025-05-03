import pandas as pd
from utils.helpers import generate_df_summary, group_bank_df, write_dfs_to_sheet
from typing import Literal


def split_df_to_ranges(
    df: pd.DataFrame, range_type: Literal["חודש", "שנה"]
) -> list[(str, pd.DataFrame)]:
    df = df.copy()
    df["תאריך"] = pd.to_datetime(df["תאריך"], dayfirst=True)
    ranges_dfs = []
    df[range_type] = df["תאריך"].dt.strftime("%b %Y" if range_type == "חודש" else "%Y")

    for range_name in df[range_type].unique():
        range_df = df[df[range_type] == range_name]
        range_df = range_df.sort_values(by="תאריך", ascending=True)
        range_df["תאריך"] = range_df["תאריך"].dt.strftime(
            "%d" if range_type == "חודש" else "%d/%m"
        )
        range_df.drop(columns=[range_type], inplace=True)
        ranges_dfs.append((range_name, range_df))
    return ranges_dfs


def create_range_summary_df(ranges_dfs: list[(str, pd.DataFrame)]):
    summary_df = pd.DataFrame()
    for range_name, range_df in ranges_dfs:
        range_summary_df = generate_df_summary(range_df)
        range_summary_df = range_summary_df.reset_index().rename(columns={'index': 'מקור', 'סכום': range_name})
        if summary_df.empty:
            summary_df = range_summary_df[['מקור']]
        summary_df[range_name] = range_summary_df[range_name]

    return summary_df


def generate_full_excel(df: pd.DataFrame):
    "this will split the df into months (m/y) and save it as an excel file, each tab in the excel file is a month"
    months_dfs = split_df_to_ranges(df, "חודש")
    months_summary_df = create_range_summary_df(months_dfs)
    
    years_dfs = split_df_to_ranges(df, "שנה")
    years_summary_df = create_range_summary_df(years_dfs)

    # all df
    full_df = df.copy()
    full_df = full_df.sort_values(by="תאריך", ascending=True)

    # Create ExcelWriter outside the loop
    with pd.ExcelWriter("full_excel.xlsx") as writer:
        write_dfs_to_sheet(
            writer,
            "all",
            [[full_df], [group_bank_df(full_df)], [generate_df_summary(full_df)]],
        )

        # write years summary
        write_dfs_to_sheet(writer, "years_summary", [[years_summary_df]])

        # write months summary
        write_dfs_to_sheet(writer, "months_summary", [[months_summary_df]])

        # write years summary
        write_dfs_to_sheet(writer, "years_summary", [[years_summary_df]])

        for year, year_df in years_dfs:
            year_summary_df = generate_df_summary(year_df)
            year_summary_df = year_summary_df.reset_index().rename(
                columns={"index": "מקור הכנסה"}
            )

            write_dfs_to_sheet(
                writer, year, [[year_df, group_bank_df(year_df)], [year_summary_df]]
            )

        for month, month_df in months_dfs:
            month_summary_df = generate_df_summary(month_df)
            month_summary_df = month_summary_df.reset_index().rename(
                columns={"index": "מקור הכנסה"}
            )
            write_dfs_to_sheet(
                writer,
                month,
                [[month_df, group_bank_df(month_df)], [month_summary_df]],
            )

    print("excel file created successfully")
