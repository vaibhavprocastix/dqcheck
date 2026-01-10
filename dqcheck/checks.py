import pandas as pd
import numpy as np

# -----------------------------
# STRUCTURAL CHECKS
# -----------------------------

def check_missing_values(df: pd.DataFrame):
    results = []
    for col in df.columns:
        missing_pct = df[col].isnull().mean() * 100
        if missing_pct > 0:
            results.append({
                "column": col,
                "issue": "missing_values",
                "missing_pct": round(missing_pct, 2),
                "severity": "high" if missing_pct > 30 else "medium"
            })
    return results


def check_duplicate_rows(df: pd.DataFrame):
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        return {
            "issue": "duplicate_rows",
            "duplicate_count": int(dup_count),
            "severity": "medium"
        }
    return None


def check_constant_columns(df: pd.DataFrame):
    results = []
    for col in df.columns:
        unique_vals = df[col].nunique(dropna=False)
        if unique_vals <= 1:
            results.append({
                "column": col,
                "issue": "constant_column",
                "unique_values": int(unique_vals),
                "severity": "high"
            })
    return results


def check_data_types(df: pd.DataFrame):
    results = []
    for col in df.columns:
        inferred_type = pd.api.types.infer_dtype(df[col], skipna=True)
        results.append({
            "column": col,
            "inferred_type": inferred_type
        })
    return results


# -----------------------------
# STATISTICAL CHECKS
# -----------------------------

def check_outliers_iqr(df: pd.DataFrame):
    results = []
    numeric_cols = df.select_dtypes(include=np.number).columns

    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outlier_pct = ((df[col] < lower) | (df[col] > upper)).mean() * 100

        if outlier_pct > 0:
            results.append({
                "column": col,
                "issue": "outliers",
                "outlier_pct": round(outlier_pct, 2),
                "severity": "high" if outlier_pct > 10 else "low"
            })

    return results
