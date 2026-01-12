import rich_click as click
import pandas as pd
from dqcheck.analyzer import run_all_checks
from dqcheck.report import save_json_report, save_html_report
from dqcheck.fixer import fix_missing_values,fix_outliers,fix_errors,fix_high_cardinality


@click.group(
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="""
dqcheck – Data Quality Intelligence Tool

Analyze and fix data quality issues before machine learning training.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

analyze
    Analyze a dataset for data quality issues such as:

        • missing values
        • outliers
        • class imbalance
        • high-cardinality features

    Usage:
        dqcheck analyze data.csv --report=html
        dqcheck analyze data.csv --report=json
        dqcheck analyze data.csv --target=label --report=both

fix
    Fix specific data quality issues.

    Supported issues & methods:

    missing_values:
        drop             Remove rows that contain missing values
        mean             Replace missing numbers with the average
        median           Replace missing numbers with the middle value
        mode             Replace missing values with the most frequent value
        constant         Replace missing values with a fixed value

    outliers:
        cap              Limit extreme values to a reasonable range
        remove           Delete rows containing extreme values
        log              Apply log transformation
        clip_percentile  Cap values using percentile limits
        zscore           Remove values far from the average

    errors:
        range_clip       Force values into a valid range
        drop_invalid     Remove rows with invalid values
        cast_type        Convert values to correct data type
        standardize_text Normalize text casing and spacing
        replace_map      Replace known incorrect values
        regex_clean      Clean values using patterns

    high_cardinality:
        drop             Remove ID-like columns
        group_rare       Group rare categories into "Other"
        frequency_encode Encode categories by frequency
        target_encode    Encode using target mean
        hashing          Hash categories into fixed bins
        extract_features Derive simpler features

    Usage:
        dqcheck fix data.csv --issue=missing_values --method=median
        dqcheck fix data.csv --issue=outliers --method=cap
        dqcheck fix data.csv --issue=high_cardinality --method=group_rare --value=20

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
)
def cli():
    pass




@cli.command()
@click.argument("data_path", type=click.Path(exists=True))
@click.option("--target", default=None, help="Target column name (optional)")
@click.option(
    "--report",
    default="json",
    type=click.Choice(["json", "html", "both"]),
    help="Report format to generate"
)
def analyze(data_path, target, report):
    click.echo(f"Loading dataset: {data_path}")

    df = pd.read_csv(data_path)

    click.echo("🔍 Running data quality checks...")
    results = run_all_checks(df, target=target)

    if report in ("json", "both"):
        save_json_report(results, "data_quality_report.json")
        click.echo("JSON report saved: data_quality_report.json")

    if report in ("html", "both"):
        save_html_report(results, "data_quality_report.html")
        click.echo("HTML report saved: data_quality_report.html")

    click.echo("\nDataset Health Score:")
    click.echo(f"   {results['scores']['dataset_score']} / 100")

    click.echo("\n✔ Analysis complete.")

@cli.command()
@click.argument("data_path", type=click.Path(exists=True))
@click.option("--issue", required=True,type=click.Choice(["missing_values", "outliers", "errors", "high_cardinality"]))
@click.option("--method", required=True, help="Fixing method")
@click.option("--value", default=None, help="Optional value for the method")
@click.option("--target", default=None, help="Target column (required for target encoding)")
def fix(data_path, issue, method, value, target):

    click.echo(f"🛠 Fixing issue: {issue}")
    df = pd.read_csv(data_path)

    # Dispatch to correct fixer
    if issue == "missing_values":
        cleaned_df, log = fix_missing_values(df, method, value)

    elif issue == "outliers":
        cleaned_df, log = fix_outliers(df, method, value)

    elif issue == "errors":
        cleaned_df, log = fix_errors(df, method, value)

    elif issue == "high_cardinality":
        cleaned_df, log = fix_high_cardinality(
            df, method, value=value, target=target
        )

    else:
        click.echo("❌ Unsupported issue type.")
        return

    # Save outputs
    cleaned_df.to_csv("cleaned_data.csv", index=False)

    import json
    with open("change_log.json", "w") as f:
        json.dump(log, f, indent=2)

    click.echo("✅ Cleaned data saved as cleaned_data.csv")
    click.echo("📜 Change log saved as change_log.json")

