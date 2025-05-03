import pandas as pd

df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
df2 = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
col_dfs_list = [df, df2]
# iterate over the col_dfs_list and print the max of len(df.columns)
