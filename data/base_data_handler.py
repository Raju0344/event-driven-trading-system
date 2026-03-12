# data.py
from __future__ import annotations
from abc import ABC, abstractmethod

import pandas as pd
from datetime import datetime
from typing import Dict, List,Any, Tuple


class DataHandler(ABC):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a DataHandler is to output a stream of bars (OHLCVI)
    for each symbol requested, emulating a live trading environment.
    """

    @abstractmethod
    def get_latest_bar(self, symbol: str) -> Any:
        """
        Return the most recent bar for a given symbol.
        """
        pass

    @abstractmethod
    def get_latest_bars(self, symbol: str, n: int = 1) -> List[Any]:
        """
        Return the last `n` bars for a given symbol.
        """
        pass

    @abstractmethod
    def get_latest_bar_datetime(self, symbol: str) -> datetime:
        """
        Return the datetime of the most recent bar.
        """
        pass

    @abstractmethod
    def get_latest_bar_value(self, symbol: str, value_type: str) -> float:
        """
        Return a specific value (open, high, low, close, volume, oi)
        from the most recent bar.
        """
        pass

    @abstractmethod
    def get_latest_bars_values(
        self, symbol: str, value_type: str, n: int = 1
    ) -> List[float]:
        """
        Return the last `n` values of `value_type` from the bars.
        """
        pass
    @abstractmethod
    def get_DataFrame(
        self, symbol: str, n: int 
    ) -> pd.DataFrame:
        """
        Return the last `n` values of `value_type` from the bars.
        """
        pass

    @abstractmethod
    def update_bars(self) -> None:
        """
        Push the next bar for each symbol to the event queue.

        Format:
        (datetime, open, high, low, close, volume, open_interest)
        """
        pass

