import pandas as pd


# sum the רווח in משכורת, מס הכנסה, מעמ, ביטוח לאומי, רואה חשבון all of them if exists
def generate_df_summary(df: pd.DataFrame) -> pd.DataFrame:
    # sum or 0 if the column is not in the df
    salary = df[df["מהות הפעולה"].isin(["משכורת"])]["רווח"].sum() or 0
    income_tax = df[df["מהות הפעולה"].isin(["מס הכנסה"])]["רווח"].sum() or 0
    vat_tax = df[df["מהות הפעולה"].isin(["מעמ"])]["רווח"].sum() or 0
    national_tax = df[df["מהות הפעולה"].isin(["ביטוח לאומי"])]["רווח"].sum() or 0
    accountant_fee = df[df["מהות הפעולה"].isin(["רואה חשבון"])]["רווח"].sum() or 0
    credit_card = df[df["מהות הפעולה"].isin(["כרטיס אשראי"])]["רווח"].sum() or 0
    transfers = (
        df[df["מהות הפעולה"].isin(["העברה נכנסת", "העברה יוצאת"])]["רווח"].sum() or 0
    )
    other_expenses = (
        df[
            ~df["מהות הפעולה"].isin([
                "משכורת",
                "מס הכנסה",
                "מעמ",
                "ביטוח לאומי",
                "רואה חשבון",
                "כרטיס אשראי",
                "העברה נכנסת",
                "העברה יוצאת",
            ])
        ]["רווח"].sum()
        or 0
    )
    net_salary = salary + income_tax + vat_tax + national_tax + accountant_fee
    # create a new df that summarizes the above
    summary_df = pd.DataFrame({
        "סכום": [
            salary,
            income_tax,
            vat_tax,
            national_tax,
            accountant_fee,
            credit_card,
            "",
            net_salary,
            "",
            transfers,
            other_expenses,
            df["רווח"].sum(),
        ]
    }, index=[
        "משכורת",
        "מס הכנסה",
        "מעמ",
        "ביטוח לאומי",
        "רואה חשבון",
        "כרטיס אשראי",
        "",
        "משכורת נטו",
        "",
        "העברות",
        "אחר",
        "סך הכל",
    ])

    return summary_df


def group_bank_df(df: pd.DataFrame):
    return (
        df.groupby("מהות הפעולה")
        .agg({"רווח": "sum", "פרטים": lambda x: ", ".join(list(set(x)))})
        .reset_index()
    )


def write_dfs_to_sheet(writer, sheet_name, dfs_list, seperation_between_df=1):
    """dfs list is a nested list, each nested list of df is a col in the df"""
    start_col_index = 0
    for col_index, col_dfs_list in enumerate(dfs_list):
        longest_df_width = (
            0
            if col_index == 0
            else max(len(df.columns) for df in dfs_list[col_index - 1])
            + seperation_between_df
        )
        start_col_index += longest_df_width

        start_row_index = 0
        for df_index, df in enumerate(col_dfs_list):
            last_df_height = (
                0
                if df_index == 0
                else col_dfs_list[df_index - 1].shape[0] + seperation_between_df + 1
            )
            start_row_index += last_df_height
            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
                startrow=start_row_index,
                startcol=start_col_index,
            )
