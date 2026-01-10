# dqcheck – Data Quality Intelligence Tool

dqcheck is a CLI-first Python tool that audits datasets before machine learning
training by detecting data quality issues and generating interpretable reports.

---

## Why This Matters

Most machine learning failures occur due to poor data quality rather than
model choice. dqcheck helps identify structural and statistical risks early,
before any ML model is trained.

---

## Features

- Structural data quality checks (missing values, duplicates, constant columns)
- Statistical anomaly detection (outliers)
- Column-level and dataset-level quality scoring
- JSON and HTML report generation
- CLI usable from terminal, Jupyter Notebook, and Google Colab

---

## Tech Stack

- Python
- Pandas, NumPy, SciPy
- Scikit-learn
- Click (CLI)
- Jinja2 (HTML reports)

---

## Installation

```bash
git clone https://github.com/<your-username>/dqcheck.git
cd dqcheck
python3 -m venv venv
source venv/bin/activate
pip install -e .
