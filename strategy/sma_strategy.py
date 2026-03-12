from __future__ import annotations

from typing import Any

import datetime
import numpy as np

from .base import Strategy
from core import SignalEvent
from utils import ConfigJson, get_logger
  
logger = get_logger("SIGNAL EVENT")

class MovingAverageCrossStrategy(Strategy):
    """
    Simple Moving Average Crossover Strategy.

    Long entry:
        Short MA crosses above Long MA

    Exit:
        Short MA crosses below Long MA
    """

    def __init__(
        self,
        bars,
        events,
        short_window: int = 5,
        long_window: int = 8,
    ):
        self.bars = bars      # Neccessary 
        self.events = events  # Neccessary
        self.symbol_list = bars.symbol_list

        self.short_window = short_window
        self.long_window = long_window

        # Track whether a symbol is currently in the market
        self.bought = {symbol: "OUT" for symbol in self.symbol_list}

    # ------------------------------------------------------------------
    # SIGNAL GENERATION
    # ------------------------------------------------------------------
    def calculate_signals(self, event) -> None:
        """
        Generate trading signals based on moving average crossover.
        """
        if event.type != "MARKET":
            return

        for symbol in self.symbol_list:
            prices = self.bars.get_latest_bars_values(
                symbol,
                value_type="close",
                n=self.long_window,
            )   # return list of the price 

            if prices is None or len(prices) < self.long_window:
                continue
            
            # print the dataframe
            #print(self.bars.get_DataFrame(symbol, self.long_window))

            short_sma = np.mean(prices[-self.short_window:])
            long_sma = np.mean(prices[-self.long_window:])

            bar_date = self.bars.get_latest_bar_datetime(symbol)
            now = datetime.datetime.utcnow()

            # --------------------------------------------------
            # BUY ENTRY
            # --------------------------------------------------
            if short_sma > long_sma and self.bought[symbol] == "OUT":
                logger.info(f"BUY SIGNAL: {symbol} @ {bar_date}")

                signal = SignalEvent(
                    strategy_id=1,
                    symbol=symbol,
                    datetime=now,
                    signal_type="BUY",
                    strength=1.0,
                )

                self.events.put(signal)  # Put the signal in the Queue
                self.bought[symbol] = "BUY"

            # --------------------------------------------------
            # EXIT
            # --------------------------------------------------
            elif short_sma < long_sma and self.bought[symbol] == "BUY":
                logger.info(f"EXIT SIGNAL: {symbol} @ {bar_date}")

                signal = SignalEvent(
                    strategy_id=1,
                    symbol=symbol,
                    datetime=now,
                    signal_type="EXIT",
                    strength=1.0,
                )

                self.events.put(signal)
                self.bought[symbol] = "OUT"

