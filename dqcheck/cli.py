import click
import pandas as pd
from dqcheck.analyzer import run_all_checks
from dqcheck.report import save_json_report, save_html_report
from dqcheck.fixer import fix_missing_values


@click.group()
def cli():
    """dqcheck: Data Quality Intelligence Tool"""
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
    """Analyze dataset for data quality issues."""
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
@click.option("--issue", required=True, help="Issue to fix (e.g., missing_values)")
@click.option("--method", required=True, help="Fixing method")
@click.option("--value", default=None, help="Value for constant fill (optional)")
def fix(data_path, issue, method, value):
    """Fix specific data quality issues (explicit user request only)."""

    if issue != "missing_values":
        click.echo("❌ Only missing_values fixing is supported for now.")
        return

    df = pd.read_csv(data_path)

    click.echo("🛠 Fixing missing values...")
    cleaned_df, log = fix_missing_values(df, method, value)

    cleaned_df.to_csv("cleaned_data.csv", index=False)

    with open("change_log.txt", "w") as f:
        f.write(str(log))

    click.echo("Cleaned data saved as cleaned_data.csv")
    click.echo("Change log saved as change_log.txt")

