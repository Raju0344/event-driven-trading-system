# performance.py
import numpy as np
import pandas as pd
from typing import Tuple


def create_sharpe_ratio(
    returns: pd.Series,
    periods: int = 252
) -> float:
    """
    Calculate the annualised Sharpe ratio assuming zero risk-free rate.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns (daily, hourly, etc.)
    periods : int, default=252
        Number of periods per year (252 = daily)

    Returns
    -------
    float
        Annualised Sharpe ratio
    """
    returns = returns.dropna()

    if returns.std() == 0:
        return 0.0

    return np.sqrt(periods) * returns.mean() / returns.std()


def create_drawdowns(
    pnl: pd.Series
) -> Tuple[pd.Series, float, int]:
    """
    Calculate drawdown series, maximum drawdown,
    and drawdown duration.

    Parameters
    ----------
    pnl : pd.Series
        Cumulative PnL or equity curve

    Returns
    -------
    drawdown : pd.Series
        Drawdown values over time
    max_drawdown : float
        Maximum drawdown
    max_duration : int
        Maximum drawdown duration
    """
    pnl = pnl.dropna()

    # High water mark
    hwm = pnl.cummax()

    # Drawdown series
    drawdown = hwm - pnl

    # Drawdown duration
    duration = (drawdown > 0).astype(int)
    duration = duration.groupby((duration == 0).cumsum()).cumsum()

    return drawdown, drawdown.max(), duration.max()
