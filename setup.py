from setuptools import setup, find_packages

setup(
    name="event-driven-trading-system",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "statsmodels",
        "mysql-connector-python",
        "kiteconnect"
    ],
    author="Raju",
    description="Event driven trading system for Indian equity market",
    python_requires=">=3.8",

    entry_points={
        "console_scripts": [
            "trader=event_driven_trading_system.cli:run",
        ],
    },
)