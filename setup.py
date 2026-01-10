from setuptools import setup, find_packages

setup(
    name="dqcheck",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scipy",
        "scikit-learn",
        "click",
        "jinja2"
    ],
    entry_points={
        "console_scripts": [
            "dqcheck=dqcheck.cli:cli"
        ]
    }
)
