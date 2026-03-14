from setuptools import setup, find_packages

setup(
    name="event-driven-trading-system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "statsmodels",
        "kiteconnect",
        "sqlalchemy",
        "pymysql",
        "mysql-connector-python"
    ],
    author="Raju",
    description="Event driven trading system for Indian equity market",
    python_requires=">=3.8",
)