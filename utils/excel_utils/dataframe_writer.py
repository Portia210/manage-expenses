"""DataFrame writing utilities."""
from typing import List
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
from .worksheet_formatter import WorksheetFormatter

class DataFrameWriter:
    """Handles writing DataFrames to Excel worksheets."""
    
    def __init__(self, writer: pd.ExcelWriter):
        self.writer = writer
        self.workbook = writer.book
    
    def _get_or_create_worksheet(self, sheet_name: str) -> Worksheet:
        """Get existing worksheet or create new one."""
        if sheet_name not in self.writer.sheets:
            _ = self.workbook.create_sheet(sheet_name)
        return self.writer.sheets[sheet_name]
    
    def write_dataframe_list(
        self,
        sheet_name: str,
        dfs_list: List[List[pd.DataFrame]],
        separation: int = 1
    ) -> None:
        """Write a nested list of DataFrames to a worksheet."""
        worksheet = self._get_or_create_worksheet(sheet_name)
        formatter = WorksheetFormatter(worksheet)
        
        start_col_index = 0
        for col_index, col_dfs_list in enumerate(dfs_list):
            # Calculate column position
            longest_df_width = (
                0 if col_index == 0
                else max(len(df.columns) for df in dfs_list[col_index - 1])
                + separation
            )
            start_col_index += longest_df_width
            
            # Write each DataFrame in the column
            start_row_index = 0
            for df_index, df in enumerate(col_dfs_list):
                # Calculate row position
                last_df_height = (
                    0 if df_index == 0
                    else col_dfs_list[df_index - 1].shape[0] + separation + 1
                )
                start_row_index += last_df_height
                
                # Write and format DataFrame
                df.to_excel(
                    self.writer,
                    sheet_name=sheet_name,
                    index=False,
                    startrow=start_row_index,
                    startcol=start_col_index,
                )
                
                formatter.format_dataframe(df, start_row_index, start_col_index) 