import pandas as pd
from dqcheck import checks
from dqcheck.scoring import score_dataset

def run_all_checks(df: pd.DataFrame, target: str | None = None):
    report = {
        "dataset": {
            "rows": df.shape[0],
            "columns": df.shape[1]
        },
        "issues": []
    }

    # Structural checks
    report["issues"].extend(checks.check_missing_values(df))
    dup = checks.check_duplicate_rows(df)
    if dup:
        report["issues"].append(dup)
    report["issues"].extend(checks.check_constant_columns(df))

    # Statistical checks
    report["issues"].extend(checks.check_outliers_iqr(df))

    report["issues"].extend(checks.check_high_cardinality(df))


    # Target-related checks (placeholder for later)
    if target and target in df.columns:
        report["target"] = target

    scores = score_dataset(df, report["issues"])
    report["scores"] = scores

    imbalance = checks.check_class_imbalance(df, target)
    if imbalance:
        report["issues"].append(imbalance)

    return report

