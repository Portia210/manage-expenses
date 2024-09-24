import pandas as pd


def _combine_horizontal(df_list: list, num_columns: int) -> pd.DataFrame:
    combined_df = pd.DataFrame()

    for i, df in enumerate(df_list):
        df = df.reset_index(drop=True)

        for j in range(0, len(df.columns), num_columns):
            column_slice = df.iloc[:, j:j + num_columns]
            combined_df = pd.concat([combined_df, column_slice], axis=1)

        if i < len(df_list) - 1:
            empty_cols = pd.DataFrame('', index=df.index, columns=[f'Empty_{i + 1}_{k}' for k in range(1, 3)])
            combined_df = pd.concat([combined_df, empty_cols], axis=1)

    combined_df.columns = [col if not col.startswith('Empty_') else '' for col in combined_df.columns]
    return combined_df


import pandas as pd


def _combine_vertical(df_list: list, num_rows: int) -> pd.DataFrame:
    max_cols = max(len(df.columns) for df in df_list)
    all_rows = []

    for i, df in enumerate(df_list):
        # Add column names as a separate row
        all_rows.append(df.columns.tolist() + [''] * (max_cols - len(df.columns)))

        # Add data rows
        for _, row in df.iterrows():
            all_rows.append(row.tolist() + [''] * (max_cols - len(df.columns)))

        # Add empty rows between DataFrames, except after the last one
        if i < len(df_list) - 1:
            all_rows.extend([[''] * max_cols] * 2)

    # Create a new DataFrame from all rows
    combined_df = pd.DataFrame(all_rows)

    return combined_df

# Example usage
df1 = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [5, 6, 7, 8],
    'C': [9, 10, 11, 12],
    'D': [13, 14, 15, 16]
})

df2 = pd.DataFrame({
    'X': ['a', 'b', 'c', 'd'],
    'Y': ['e', 'f', 'g', 'h'],
    'Z': ['i', 'j', 'k', 'l']
})

df_list = [df1, df2]

# Vertical combination
result_horizontal = _combine_horizontal(df_list, num_columns=4)
# result_vertical = _combine_vertical([result_horizontal, df2], num_rows=4)
# new_result = _combine_horizontal([result_vertical, df2], num_columns=1)
print("Vertical combination:")
# print(new_result)

# Save to CSV
result_horizontal.to_csv("master.csv", index=False)