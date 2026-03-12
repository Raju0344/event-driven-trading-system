# main.py
from __future__ import annotations

import time
import json
import os
import pprint
import datetime
import sys
from typing import List, Type
from queue import Queue, Empty

from utils import get_logger

logger = get_logger("ENGINE")


class Engine:
    """
    Encapsulates the settings and components for carrying out
    an event-driven backtest.
    """
    def __init__(
        self,
        symbol_list: List[str],
        initial_capital: float,
        heartbeat: float,
        start_date: datetime,
        data_handler_class,
        execution_handler_class,
        portfolio_class,
        strategy_class,
        db_engine,
        mapper = None,
        kit = None

    ):
        """
        Parameters
        ----------
        csv_dir : str
            Root directory for CSV data
        symbol_list : list[str]
            Symbols to backtest
        initial_capital : float
            Starting portfolio capital
        heartbeat : float
            Time delay between iterations (seconds)
        start_date : datetime
            Backtest start date
        data_handler_cls : class
            Market data handler
        execution_handler_cls : class
            Order execution handler
        portfolio_cls : class
            Portfolio handler
        strategy_cls : class
            Trading strategy
        """
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date
        self.db_engine = db_engine
        self.mapper = mapper
        self.kite = kit
        

        self.data_handler_class = data_handler_class
        self.execution_handler_class = execution_handler_class
        self.portfolio_class = portfolio_class
        self.strategy_class = strategy_class

        self.events: Queue = Queue()
        self.live_iter = 0
        self.signals = 0
        self.orders = 0
        self.fills = 0

        self._generate_trading_instances()

    # ------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------
    def _generate_trading_instances(self) -> None:
        """
        Instantiate all trading components.
        """
        logger.info("Started Trading System")
        logger.info("Creating DataHandler, Strategy, Portfolio, ExecutionHandler")
        # 1. DataHandler
        self.data_handler = self.data_handler_class(
            self.events, self.symbol_list, self.db_engine, self.mapper
        )
        # 2. Strategy
        self.strategy = self.strategy_class(
            self.data_handler, self.events
        )
        # 3. portfolio
        self.portfolio = self.portfolio_class(
            self.data_handler,
            self.events,
            self.start_date,
            self.initial_capital,
        )
        # 4. execution handler
        self.execution_handler = self.execution_handler_class(self.events, self.kite)
    

    # ------------------------------------------------------------------
    # BACKTEST LOOP
    # ------------------------------------------------------------------
    def _run_backtest(self) -> None:
        """
        Execute the event-driven backtest.
        """
        iteration = 0

        while True:  # Iteration loop
            iteration += 1
            logger.info(f"ITERATION {iteration}")

            # Update market data 
            if self.data_handler.continue_backtest:
                self.data_handler.update_bars()  # updating the bar
            else:
                break

            # events process loop (This loop run untill the event Queue get Empty)
            while True:
                try:
                    event = self.events.get_nowait()
                except Empty:
                    break
                else:
                    if event is None:
                        continue

                    if event.type == "MARKET":
                        self.strategy.calculate_signals(event) # strategy calculate the signal(it will create signal)
                        self.portfolio.update_timeindex()      

                    elif event.type == "SIGNAL":
                        self.signals += 1
                        self.portfolio.update_signal(event)

                    elif event.type == "ORDER":
                        self.orders += 1
                        self.execution_handler.execute_order(event)

                    elif event.type == "FILL":
                        self.fills += 1
                        self.portfolio.update_fill(event)

            time.sleep(self.heartbeat)

    # ------------------------------------------------------------------
    # LIVE LOOP
    # ------------------------------------------------------------------
    def _run_live(self) -> None:
        """
        Execute the event-driven live trading.
        """
        # Update market data 
        self.data_handler.update_bars()  # updating the bar(it will create the market event)

        bar_price = self.data_handler.get_latest_bar_value(self.symbol_list[0], "close")
        bar_time = self.data_handler.get_latest_bar_datetime(self.symbol_list[0])
        self.live_iter +=1
        logger.info(f"ITERATION {self.live_iter} | {bar_time} | {bar_price}")


        # events process loop (This loop run untill the event Queue get Empty)
        while True:
            try:
                event = self.events.get_nowait()
            except Empty:
                break
            else:
                if event is None:
                    continue

                if event.type == "MARKET":
                    self.strategy.calculate_signals(event) # strategy calculate the signal(it will create signal)
                    self.portfolio.update_timeindex() 
                    if self.portfolio.is_market_close():
                        self.portfolio.close_all_positions()     

                elif event.type == "SIGNAL":
                    self.signals += 1
                    self.portfolio.update_signal(event)

                elif event.type == "ORDER":
                    self.orders += 1
                    self.execution_handler.execute_order(event)

                elif event.type == "FILL":
                    self.fills += 1
                    self.portfolio.update_fill(event)


    # ------------------------------------------------------------------
    # PERFORMANCE OUTPUT
    # ------------------------------------------------------------------
    def _output_performance(self) -> List:
        """
        Output backtest performance statistics.
        """
        self.portfolio.create_equity_curve_dataframe()

        print("\nCreating summary statistics...\n")
        stats = self.portfolio.output_summary_stats()

        print("\nEquity Curve (tail):\n")
        print(self.portfolio.equity_curve.tail(10))

        print("\nPerformance Metrics:\n")
        pprint.pprint(stats)

        events = [("Signals", f"{self.signals}"),
                ("Orders" , f"{self.orders}"),
                ("Fills"  , f"{self.fills}")]
        
        print("\nEvent Counts:")
        pprint.pprint(events)
        
        return stats, events

    # ------------------------------------------------------------------
    # SIMULATE TRADING
    # ------------------------------------------------------------------
    def simulate_trading(self) -> None:
        """
        Run the full backtest and output performance.
        """
        self._run_backtest()

    # ------------------------------------------------------------------
    # LIVE TRADING
    # ------------------------------------------------------------------
    def live_trading(self) -> None:
        """
        Run the full backtest and output performance.
        """
        pass
            










