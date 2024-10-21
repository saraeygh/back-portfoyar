import pandas as pd


def filter_rows_with_nan_values(df: pd.DataFrame, col_list: list):
    nan_rows = df[col_list].isna().any(axis=1)
    filtered_rows = df[~nan_rows]

    return filtered_rows
