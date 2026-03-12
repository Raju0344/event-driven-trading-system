from __future__ import annotations

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
#import datetime
from datetime import  datetime, timezone
from typing import Dict, List,Any, Iterator, Tuple
from core import MarketEvent
from .base_data_handler import DataHandler

from utils import get_logger

Bar = Tuple[datetime, pd.Series]

logger = get_logger("Market Event")


class HistoricMySQLDataHandler(DataHandler):
    """
    HistoricMySQLDataHandler reads OHLCV data from MySQL
    and provides a streaming interface identical to live trading.
    """

    def __init__(
        self,
        events,                   
        symbol_list: List[str],
        db_engine,
        kite = None
    ):
        self.events = events
        self.symbol_list = symbol_list
        self.db_engine= db_engine

        self.symbol_data: Dict[str, Iterator[Bar]] = {}  # iterator data 
        self.latest_symbol_data: Dict[str, List[Bar]] = {}  # latest data

        self.continue_backtest: bool = True

        self._open_convert_mysql_data()

    # ------------------------------------------------------------
    # MYSQL LOADING
    # ------------------------------------------------------------
    def _open_convert_mysql_data(self) -> None:
        """
        Load OHLCV data from MySQL into pandas DataFrames,
        align indices, and convert to iterators.
        """
        combined_index = None
        for symbol in self.symbol_list:
            query = """
            SELECT
                p.price_time AS datetime,
                p.close_price AS close,
                p.high_price AS high,
                p.low_price AS low,
                p.open_price AS open,
                p.volume
            FROM price_table p
            JOIN symbol_table s ON p.symbol_id = s.id
            WHERE s.ticker = %s
            ORDER BY p.price_time
            """

            df = pd.read_sql(
                query,
                self.db_engine,
                params=(symbol,),
                parse_dates=["datetime"],
            )

            if df.empty:
                logger.error(f"No price data found for symbol {symbol}")

            df.set_index("datetime", inplace=True)

            # FORCE numeric conversion (same safety as CSV version)
            numeric_cols = ["open", "high", "low", "close", "volume"]
            df[numeric_cols] = df[numeric_cols].apply(
                pd.to_numeric, errors="coerce"
            )

            df = df.dropna()
            df = df.sort_index()

            self.symbol_data[symbol] = df
            self.latest_symbol_data[symbol] = [] # initialise the latest_symbol_data

            if combined_index is None:
                combined_index = df.index
            else:
                combined_index = combined_index.union(df.index) # taking union of the combine index

        # Reindex and convert to iterators (EXACTLY like CSV version)
        for symbol in self.symbol_list:
            self.symbol_data[symbol] = (
                self.symbol_data[symbol]
                .reindex(index=combined_index, method="pad")
                .iterrows()
            )
            # iterator convert DataFrame to tuple(timeindex, pd.Series)


    # ------------------------------------------------------------
    # BAR ACCESS METHODS
    # ------------------------------------------------------------
    def _get_new_bar(self, symbol: str) -> Iterator[Bar]:
        """
        Generator yielding the next bar for a symbol.
        """
        for bar in self.symbol_data[symbol]:
            yield bar

    def get_latest_bar(self, symbol: str) -> Bar:
        return self.latest_symbol_data[symbol][-1]

    # get_latest_bars data   
    def get_latest_bars(self, symbol: str, n: int = 1) -> List[Bar]:
        return self.latest_symbol_data[symbol][-n:]

    def get_latest_bar_datetime(self, symbol: str) -> datetime:
        return self.get_latest_bar(symbol)[0]

    def get_latest_bar_value(self, symbol: str, value_type: str) -> float:
        return getattr(self.get_latest_bar(symbol)[1], value_type)
    
    # get_latest_bars_values upto the n(look back)
    def get_latest_bars_values(
        self, symbol: str, value_type: str, n: int = 1
    ) -> np.ndarray:
        bars = self.get_latest_bars(symbol, n)
        return np.array([getattr(bar[1], value_type) for bar in bars])  # adj_close
    
    def get_DataFrame(self, symbol, n):
        return pd.DataFrame([row[1] for row in self.latest_symbol_data[symbol][-n:]], index = [row[0] for row in self.latest_symbol_data[symbol][-n:]])

    # ------------------------------------------------------------
    # EVENT UPDATE
    # ------------------------------------------------------------
    def update_bars(self) -> None:
        """
        Push the next bar for all symbols onto the event queue.
        """
        for symbol in self.symbol_list:
            try:
                bar = next(self._get_new_bar(symbol))  # iterate the bar using next and yield(ram efficient)
            except StopIteration:
                self.continue_backtest = False
                return
            else:
                self.latest_symbol_data[symbol].append(bar)

        self.events.put(MarketEvent()) # put the market event in the Queue

