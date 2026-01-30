"""
Excel reader module for reading Excel files into pandas DataFrames.
"""

import pandas as pd
from openpyxl import load_workbook

def read_excel(file_path: str,sheet_name=0) -> pd.DataFrame:
    """
    Read an Excel file and return its contents as a pandas DataFrame.

    Args:
        file_path: Path to the Excel file to read.

    Returns:
        pd.DataFrame: Contents of the Excel file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file cannot be parsed as Excel.
        Exception: Other errors from pandas/openpyxl.
    """
    wb = load_workbook(file_path, data_only=True)  # data_only=True 读取单元格计算后的值
    try:
        if isinstance(sheet_name, int):
            ws = wb.worksheets[sheet_name]
        else:
            ws = wb[sheet_name]
        df = pd.read_excel(file_path, engine="openpyxl")
        # 3. 遍历所有合并单元格，填充值到所有合并位置
        for merged_range in ws.merged_cells.ranges:
            # 获取合并单元格的范围（如A1:A3）
            min_col, min_row, max_col, max_row = merged_range.bounds

            # 转换为pandas的索引（注意：openpyxl是1-based，pandas是0-based）
            start_row = min_row - 2  # Excel行号-2 = DataFrame行索引（表头占1行）
            end_row = max_row - 2
            start_col = min_col - 1
            end_col = max_col - 1

            # 跳过表头外的无效行（如合并范围超出数据行数）
            if start_row >= len(df):
                continue

            # 获取合并单元格的基准值（左上角单元格的值）
            base_value = df.iloc[start_row, start_col]

            # 填充整个合并范围的所有单元格
            for row in range(start_row, min(end_row + 1, len(df))):
                for col in range(start_col, min(end_col + 1, len(df.columns))):
                    df.iloc[row, col] = base_value

        # 关闭工作簿，释放资源
    finally:
        wb.close()
    return df

