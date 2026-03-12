from __future__ import annotations

import pandas as pd
#import datetime
from datetime import  datetime, timezone
from typing import Dict, List,Any, Iterator, Tuple
from core import MarketEvent
from .base_data_handler import DataHandler



class LiveZerodhaDataHandler(DataHandler):
    """
    Live market data handler using Zerodha WebSocket (KiteTicker)
    """

    def __init__(
        self,
        events,
        symbol_list: List[str],
        tick_db,
        kite
    ):
        self.events = events
        self.symbol_list = symbol_list
        self.tick_db = tick_db
        self.mapper = kite

        self.latest_symbol_data: Dict[str, pd.DataFrame] = {
            s: [] for s in symbol_list
        }

    #------------------------------------------------
    # FETCH OHLCV DATA
    #---------------------------------------------
    #def fetchOHLC(self, symbol,interval,duration):
    #    """extracts historical data and outputs in the form of dataframe"""
    #    instrument = self.mapper.symbol_to_token(symbol)
    #    data = pd.DataFrame(kite.historical_data(instrument,datetime.date.today()-datetime.timedelta(duration), datetime.date.today(),interval))
    #    data.set_index("date",inplace=True)
    #    return data
    
    # --------------------------------------------------
    # Update Bars
    # --------------------------------------------------
    def update_bars(self):
        """
        Live mode → bars come from websocket
        """
        for symbol in self.symbol_list:
            token = self.mapper.symbol_to_token(symbol)
            if token == -1:
                continue

            df = self.tick_db.fetch_ticks_since(token)

            if df.empty:
                continue

            df = df.set_index("ts")
            df = df["price"].resample("5min").ohlc().dropna()
            df["datetime"] = df.index
            self.latest_symbol_data[symbol] = df
            self.events.put(MarketEvent()) # put the market event in the Queue
            # STRATEGY / SIGNAL HOOK GOES HERE

    def get_latest_bar(self, symbol):         # it will return the latest last bar     
        return self.latest_symbol_data[symbol].iloc[-1]

    def get_latest_bars(self, symbol, n=1):         # it will return the latest bars
        return self.latest_symbol_data[symbol].iloc[-n:]

    def get_latest_bar_datetime(self, symbol):
        return self.get_latest_bar(symbol)["datetime"]

    def get_latest_bar_value(self, symbol, value_type):
        return self.get_latest_bar(symbol)[value_type]

    def get_latest_bars_values(self, symbol, value_type, n=1):
        bars = self.get_latest_bars(symbol, n)
        return bars[value_type].to_list()
    
    def get_DataFrame(self, symbol, n):
        return self.latest_symbol_data[symbol].iloc[-n:]



