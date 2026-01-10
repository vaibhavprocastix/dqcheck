import click
import pandas as pd
from dqcheck.analyzer import run_all_checks
from dqcheck.report import save_json_report, save_html_report


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
    click.echo(f"📊 Loading dataset: {data_path}")

    df = pd.read_csv(data_path)

    click.echo("🔍 Running data quality checks...")
    results = run_all_checks(df, target=target)

    if report in ("json", "both"):
        save_json_report(results, "data_quality_report.json")
        click.echo("✅ JSON report saved: data_quality_report.json")

    if report in ("html", "both"):
        save_html_report(results, "data_quality_report.html")
        click.echo("✅ HTML report saved: data_quality_report.html")

    click.echo("\n📈 Dataset Health Score:")
    click.echo(f"   {results['scores']['dataset_score']} / 100")

    click.echo("\n✔ Analysis complete.")
