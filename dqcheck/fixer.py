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

def fix_outliers(df: pd.DataFrame, method: str, value=None):
    """
    Fix outliers in numeric columns using specified method.
    Returns cleaned dataframe and change log.
    """
    cleaned_df = df.copy()
    change_log = []

    numeric_cols = cleaned_df.select_dtypes(include=np.number).columns

    for col in numeric_cols:
        series = cleaned_df[col].dropna()

        if series.empty:
            continue

        entry = {"column": col, "method": method}

        # IQR calculation
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outlier_mask = (cleaned_df[col] < lower) | (cleaned_df[col] > upper)
        outlier_count = int(outlier_mask.sum())

        if outlier_count == 0:
            continue

        entry["outliers_before"] = outlier_count

        # ---------- METHODS ----------

        if method == "cap":
            cleaned_df.loc[cleaned_df[col] < lower, col] = lower
            cleaned_df.loc[cleaned_df[col] > upper, col] = upper
            entry["cap_lower"] = lower
            entry["cap_upper"] = upper

        elif method == "remove":
            cleaned_df = cleaned_df[~outlier_mask]
            entry["rows_removed"] = outlier_count

        elif method == "log":
            cleaned_df[col] = np.log1p(cleaned_df[col])
            entry["transform"] = "log1p"

        elif method == "clip_percentile":
            low_p = float(value.split(",")[0])
            high_p = float(value.split(",")[1])
            low_val = series.quantile(low_p)
            high_val = series.quantile(high_p)
            cleaned_df[col] = cleaned_df[col].clip(low_val, high_val)
            entry["clip_range"] = f"{low_p}-{high_p}"

        elif method == "zscore":
            mean = series.mean()
            std = series.std()
            z_mask = ((cleaned_df[col] - mean).abs() / std) > 3
            cleaned_df = cleaned_df[~z_mask]
            entry["rows_removed"] = int(z_mask.sum())

        else:
            continue

        change_log.append(entry)

    return cleaned_df, change_log
