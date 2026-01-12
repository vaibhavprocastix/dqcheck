import pandas as pd
import numpy as np


def fix_missing_values(df: pd.DataFrame, method: str, value=None):
    """
    Fix missing values using a specified method.
    Returns cleaned dataframe and change log.
    """
    cleaned_df = df.copy()
    change_log = []

    # Normalize blanks to NaN
    cleaned_df.replace(r"^\s*$", np.nan, regex=True, inplace=True)

    for col in cleaned_df.columns:
        missing_count = cleaned_df[col].isnull().sum()
        if missing_count == 0:
            continue

        entry = {
            "column": col,
            "missing_before": int(missing_count),
            "method": method
        }

        # Numeric columns
        if pd.api.types.is_numeric_dtype(cleaned_df[col]):
            if method == "mean":
                fill_value = cleaned_df[col].mean()
            elif method == "median":
                fill_value = cleaned_df[col].median()
            elif method == "drop":
                cleaned_df = cleaned_df.dropna(subset=[col])
                entry["rows_dropped"] = int(missing_count)
                change_log.append(entry)
                continue
            elif method == "constant":
                fill_value = value
            else:
                continue

        # Categorical columns
        else:
            if method == "mode":
                fill_value = cleaned_df[col].mode().iloc[0]
            elif method == "constant":
                fill_value = value
            elif method == "drop":
                cleaned_df = cleaned_df.dropna(subset=[col])
                entry["rows_dropped"] = int(missing_count)
                change_log.append(entry)
                continue
            else:
                continue

        cleaned_df[col].fillna(fill_value, inplace=True)
        entry["fill_value"] = fill_value
        change_log.append(entry)

    return cleaned_df, change_log
