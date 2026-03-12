from __future__ import annotations

from typing import Any

import datetime
import numpy as np
import statsmodels.api as sm

from .base import Strategy
from core import SignalEvent
from utils import ConfigJson, get_logger

logger = get_logger("SIGNAL EVENT")
  

class MeanRevertingPairStrategy(Strategy):

    def __init__(
        self,
        bars,
        events,
        ols_window=50,
        zscore_low=0.5,
        zscore_high=3.0
    ):
        self.bars = bars      # Neccessary 
        self.events = events  # Neccessary
        self.symbol_list = bars.symbol_list # Neccessary
        
        # additional
        self.ols_window = ols_window
        self.zscore_low = zscore_low
        self.zscore_high = zscore_high
        self.pair = ("YESBANK", "PSB")

        self.long_market = False
        self.short_market = False

    # ------------------------------------------------------------------
    # SIGNAL GENERATION
    # ------------------------------------------------------------------
    def calculate_signals(self, event) -> None:
        """
        Generate trading signals based on moving average crossover.
        """
        if event.type != "MARKET":
            return

        y = self.bars.get_latest_bars_values(self.pair[0], "close", self.ols_window)
        x = self.bars.get_latest_bars_values(self.pair[1], "close", self.ols_window)

        if y is not None and x is not None:
            # Check that all window perios are available 
            if len(y) >= self.ols_window and len(x) >= self.ols_window:
                # Calculate the current hedge ratio using OLS
                self.hedge_ratio = sm.OLS(y, x).fit().params[0]

                # Calcualte the current z-score of the residuals
                spread = y - self.hedge_ratio*x
                zscore_last = ((spread - spread.mean())/spread.std())[-1]

                # Calculate signal and add to events queue
                y_signal, x_signal = self.calculate_xy_signals(zscore_last)
                if y_signal is not None and x_signal is not None:
                    self.events.put(y_signal)
                    self.events.put(x_signal)


    def calculate_xy_signals(self, zscore_last):

        y_signal = None
        x_signal = None
        p0 = self.pair[0]
        p1 = self.pair[1]
        dt = datetime.datetime.utcnow()
        bar_date = self.bars.get_latest_bar_datetime(p0)
        hr = abs(self.hedge_ratio)

        # If we're long the market and below the negative of the high zscore thersold
        if zscore_last <= -self.zscore_high and not self.long_market:
            self.long_market = True
            y_signal = SignalEvent(1, p0, dt, "BUY", 1.0)
            x_signal = SignalEvent(1, p1, dt, "SELL", hr)
            logger.info(f"BUY SIGNAL: {p0} @ {bar_date}")
            logger.info(f"SELL SIGNAL: {p1} @ {bar_date}")

        # If we're long the market and between the absolut value of hte low zscore thresold
        if abs(zscore_last) <= self.zscore_low and self.long_market:
            self.long_market = False
            y_signal = SignalEvent(1, p0, dt, "EXIT", 1.0)
            x_signal = SignalEvent(1, p1, dt, "EXIT", 1.0)
            logger.info(f"EXIT SIGNAL: {p0} @ {bar_date}")
            logger.info(f"EXIT SIGNAL: {p1} @ {bar_date}")

        # If we're short the market and above the hgih zscore thresold 
        if zscore_last >= self.zscore_high and not self.short_market:
            self.short_market = True
            y_signal = SignalEvent(1, p0, dt, "SELL", 1.0)
            x_signal = SignalEvent(1, p1, dt, "BUY", hr)
            logger.info(f"SELL SIGNAL: {p0} @ {bar_date}")
            logger.info(f"BUY SIGNAL: {p1} @ {bar_date}")

        # If we're short the market and between the absoute value of the low zscore thresold
        if abs(zscore_last) <= self.zscore_low and self.short_market:
            self.short_market = False
            y_signal = SignalEvent(1, p0, dt, "EXIT", 1.0)
            x_signal = SignalEvent(1, p1, dt, "EXIT", 1.0)
            logger.info(f"EXIT SIGNAL: {p0} @ {bar_date}")
            logger.info(f"EXIT SIGNAL: {p1} @ {bar_date}")
        
        return y_signal, x_signal


