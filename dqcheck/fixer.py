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


def fix_errors(df: pd.DataFrame, method: str, value=None):
    """
    Fix invalid / inconsistent data values.
    Returns cleaned dataframe and change log.
    """
    cleaned_df = df.copy()
    change_log = []

    # ---------- METHOD: RANGE CLIP ----------
    if method == "range_clip":
        # value format: column:min,max
        col, min_val, max_val = value.split(":")
        min_val, max_val = float(min_val), float(max_val)

        invalid_mask = (cleaned_df[col] < min_val) | (cleaned_df[col] > max_val)
        count = int(invalid_mask.sum())

        cleaned_df.loc[cleaned_df[col] < min_val, col] = min_val
        cleaned_df.loc[cleaned_df[col] > max_val, col] = max_val

        change_log.append({
            "column": col,
            "method": "range_clip",
            "invalid_before": count,
            "range": f"{min_val}-{max_val}"
        })

    # ---------- METHOD: DROP INVALID ----------
    elif method == "drop_invalid":
        col, min_val = value.split(":")
        min_val = float(min_val)

        invalid_mask = cleaned_df[col] < min_val
        count = int(invalid_mask.sum())

        cleaned_df = cleaned_df[~invalid_mask]

        change_log.append({
            "column": col,
            "method": "drop_invalid",
            "rows_removed": count
        })

    # ---------- METHOD: CAST TYPE ----------
    elif method == "cast_type":
        # value format: column:type
        col, dtype = value.split(":")

        before_errors = cleaned_df[col].isnull().sum()

        if dtype == "int":
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce").astype("Int64")
        elif dtype == "float":
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")
        elif dtype == "string":
            cleaned_df[col] = cleaned_df[col].astype(str)

        after_errors = cleaned_df[col].isnull().sum()

        change_log.append({
            "column": col,
            "method": "cast_type",
            "type": dtype,
            "nulls_after": int(after_errors)
        })

    # ---------- METHOD: STANDARDIZE TEXT ----------
    elif method == "standardize_text":
        # value format: column
        col = value
        cleaned_df[col] = cleaned_df[col].str.strip().str.lower()

        change_log.append({
            "column": col,
            "method": "standardize_text"
        })

    # ---------- METHOD: REPLACE MAP ----------
    elif method == "replace_map":
        # value format: column:key1=val1,key2=val2
        col, mappings = value.split(":")
        replace_dict = dict(m.split("=") for m in mappings.split(","))

        cleaned_df[col] = cleaned_df[col].replace(replace_dict)

        change_log.append({
            "column": col,
            "method": "replace_map",
            "mapping": replace_dict
        })

    # ---------- METHOD: REGEX CLEAN ----------
    elif method == "regex_clean":
        # value format: column:pattern
        col, pattern = value.split(":")
        cleaned_df[col] = cleaned_df[col].str.replace(pattern, "", regex=True)

        change_log.append({
            "column": col,
            "method": "regex_clean",
            "pattern": pattern
        })

    else:
        return cleaned_df, change_log

    return cleaned_df, change_log
