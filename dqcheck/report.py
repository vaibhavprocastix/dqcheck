import json
from pathlib import Path
from jinja2 import Template

def normalize_issue(issue: dict):
    """
    Normalize issue details for HTML rendering:
    - % for missing / outliers / imbalance
    - unique count for high cardinality
    """
    clean = {}

    clean["issue"] = issue.get("issue")
    clean["column"] = issue.get("column")
    clean["severity"] = issue.get("severity")

    # Handle high cardinality separately
    if issue.get("issue") == "high_cardinality":
        clean["pct"] = f'{issue.get("unique_values")} unique'

    # Missing values
    elif "missing_pct" in issue:
        clean["pct"] = f'{round(issue["missing_pct"], 2)} %'

    # Outliers
    elif "outlier_pct" in issue:
        clean["pct"] = f'{round(issue["outlier_pct"], 2)} %'

    # Class imbalance
    elif "dominant_class_ratio" in issue:
        clean["pct"] = f'{round(issue["dominant_class_ratio"], 2)} %'

    else:
        clean["pct"] = "-"

    return clean




def save_json_report(report: dict, output_path: str):
    path = Path(output_path)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)


def save_html_report(report: dict, output_path: str):
    html_template = """
    <html>
    <head>
        <title>Data Quality Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #2c3e50; }
            .score { font-size: 22px; font-weight: bold; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #f4f4f4; }
            .high { color: red; }
            .medium { color: orange; }
            .low { color: green; }
        </style>
    </head>
    <body>
        <h1>Data Quality Report</h1>

        <p><b>Rows:</b> {{ rows }} | <b>Columns:</b> {{ cols }}</p>

        <p class="score">
            Dataset Health Score: {{ dataset_score }} / 100
        </p>

        <h2>Column Quality Scores</h2>
        <table>
            <tr>
                <th>Column</th>
                <th>Score</th>
            </tr>
            {% for col, score in column_scores.items() %}
            <tr>
                <td>{{ col }}</td>
                <td>{{ score }}</td>
            </tr>
            {% endfor %}
        </table>

        <h2>Detected Issues</h2>
        <table>
            <tr>
                <th>Issue</th>
                <th>Column</th>
                <th>Severity</th>
                <th>Impact</th>
            </tr>
            {% for issue in issues %}
            <tr>
                <td>{{ issue.issue }}</td>
                <td>{{ issue.column if issue.column else '-' }}</td>
                <td class="{{ issue.severity }}">{{ issue.severity }}</td>
                <td>{{ issue.pct }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """

    template = Template(html_template)

    clean_issues = [normalize_issue(i) for i in report["issues"]]

    html = template.render(
        rows=report["dataset"]["rows"],
        cols=report["dataset"]["columns"],
        dataset_score=report["scores"]["dataset_score"],
        column_scores=report["scores"]["column_scores"],
        issues=clean_issues
    )


    path = Path(output_path)
    with open(path, "w") as f:
        f.write(html)
