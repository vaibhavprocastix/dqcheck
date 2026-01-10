def score_column(column_name, issues):
    """
    Start with score 100 and deduct points based on issues.
    """
    score = 100

    for issue in issues:
        if issue.get("column") != column_name:
            continue

        if issue["issue"] == "missing_values":
            score -= issue["missing_pct"] * 0.5

        elif issue["issue"] == "constant_column":
            score -= 50

        elif issue["issue"] == "outliers":
            score -= issue["outlier_pct"] * 0.3

    return max(round(score, 2), 0)


def score_dataset(df, issues):
    """
    Dataset score = average of column scores,
    penalized by dataset-level issues.
    """
    column_scores = {}

    for col in df.columns:
        column_scores[col] = score_column(col, issues)

    dataset_score = sum(column_scores.values()) / len(column_scores)

    # Penalize duplicates
    for issue in issues:
        if issue.get("issue") == "duplicate_rows":
            dataset_score -= 5

    return {
        "dataset_score": round(max(dataset_score, 0), 2),
        "column_scores": column_scores
    }
