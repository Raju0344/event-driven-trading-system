# portfolio.py
from __future__ import annotations

from datetime import datetime
from math import floor
from typing import Dict, List

import numpy as np
import pandas as pd

from core import FillEvent, OrderEvent, SignalEvent
from risk import QuantityManager
from utils import ConfigJson as config
from .performance import create_sharpe_ratio, create_drawdowns


class Portfolio:
    """
    The Portfolio class manages positions, holdings and equity curve
    at each bar resolution.
    """

    def __init__(
        self,
        bars,
        events,
        start_date: datetime,
        initial_capital: float = 100_000.0,
    ):
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital
        self.quantity_manager = QuantityManager(self.initial_capital)

        # Positions
        self.all_positions = self._construct_all_positions()
        self.current_positions = {symbol: 0 for symbol in self.symbol_list}

        # Holdings
        self.all_holdings = self._construct_all_holdings()
        self.current_holdings = self._construct_current_holdings()

        self.equity_curve: pd.DataFrame | None = None

    # ------------------------------------------------------------------
    # CONSTRUCTION METHODS
    # ------------------------------------------------------------------
    def _construct_all_positions(self) -> List[dict]:
        d = {symbol: 0 for symbol in self.symbol_list}
        d["datetime"] = self.start_date
        return [d]

    def _construct_all_holdings(self) -> List[dict]:
        d = {symbol: 0.0 for symbol in self.symbol_list}
        d.update(
            {
                "datetime": self.start_date,
                "cash": self.initial_capital,
                "commission": 0.0,
                "total": self.initial_capital,
            }
        )
        return [d]

    def _construct_current_holdings(self) -> dict:
        d = {symbol: 0.0 for symbol in self.symbol_list}
        d.update(
            {
                "cash": self.initial_capital,
                "commission": 0.0,
                "total": self.initial_capital,
            }
        )
        return d

    # ------------------------------------------------------------------
    # TIME INDEX UPDATE
    # ------------------------------------------------------------------
    def update_timeindex(self) -> None:
        """
        Update positions and holdings at the current bar.
        """
        latest_dt = self.bars.get_latest_bar_datetime(self.symbol_list[0])

        # Update positions
        pos = {symbol: self.current_positions[symbol] for symbol in self.symbol_list}
        pos["datetime"] = latest_dt
        self.all_positions.append(pos)

        # Update holdings
        hold = {symbol: 0.0 for symbol in self.symbol_list}
        hold["datetime"] = latest_dt
        hold["cash"] = self.current_holdings["cash"]
        hold["commission"] = self.current_holdings["commission"]
        hold["total"] = self.current_holdings["cash"]

        for symbol in self.symbol_list:
            market_value = (
                self.current_positions[symbol]
                * self.bars.get_latest_bar_value(symbol, "close") # adj_close
            )
            hold[symbol] = market_value
            hold["total"] += market_value

        self.all_holdings.append(hold)

    # ------------------------------------------------------------------
    # FILL HANDLING
    # ------------------------------------------------------------------
    def update_positions_from_fill(self, fill: FillEvent) -> None:
        direction = 1 if fill.direction == "BUY" else -1
        self.current_positions[fill.symbol] += direction * fill.quantity

    def update_holdings_from_fill(self, fill: FillEvent) -> None:
        direction = 1 if fill.direction == "BUY" else -1
        price = self.bars.get_latest_bar_value(fill.symbol, "close")
        cost = direction * price * fill.quantity

        self.current_holdings[fill.symbol] += cost
        self.current_holdings["commission"] += fill.commission
        self.current_holdings["cash"] -= (cost + fill.commission)

    def update_fill(self, event: FillEvent) -> None:
        if event.type == "FILL":
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    # ------------------------------------------------------------------
    # ORDER GENERATION
    # ------------------------------------------------------------------
    def generate_naive_order(self, signal: SignalEvent) -> OrderEvent | None:
        symbol = signal.symbol
        direction = signal.signal_type
        cur_qty = self.current_positions[symbol]
        
        price = self.bars.get_latest_bar_value(symbol, "close")
        quantity = self.quantity_manager.calculate_quantity(price)

        if direction == "BUY" and cur_qty == 0:
            return OrderEvent(symbol, "MARKET", quantity, "BUY", "ENTRY")

        if direction == "SELL" and cur_qty == 0:
            return OrderEvent(symbol, "MARKET", quantity, "BUY", "ENTRY")

        if direction == "EXIT" and cur_qty > 0:
            return OrderEvent(symbol, "MARKET", abs(cur_qty), "SELL", "EXIT")

        if direction == "EXIT" and cur_qty < 0:
            return OrderEvent(symbol, "MARKET", abs(cur_qty), "BUY", "EXIT")

        return None

    def update_signal(self, event: SignalEvent) -> None:
        if event.type == "SIGNAL":
            order = self.generate_naive_order(event)
            if order:
                self.events.put(order)
    
    def is_market_close(self) -> bool:
        """
        Check if current bar time >= 15:30
        """
        latest_dt = self.bars.get_latest_bar_datetime(
            self.symbol_list[0]
        )
        market_close = latest_dt.replace(
            hour=15, minute=20, second=0, microsecond=0
        )
        return latest_dt >= market_close
    

    def close_all_positions(self):
        """
        Generate EXIT orders for all open positions
        """
        print("🔔 Market closing — exiting all positions")

        for symbol, qty in self.current_positions.items():
            if qty != 0:
                direction = "SELL" if qty > 0 else "BUY"
                order = OrderEvent(
                    symbol=symbol,
                    order_type="MARKET",
                    quantity=abs(qty),
                    direction=direction,
                    entry_exit="EXIT"
                )
                self.events.put(order)

    # ------------------------------------------------------------------
    # PERFORMANCE METRICS
    # ------------------------------------------------------------------
    def create_equity_curve_dataframe(self) -> None:
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index("datetime", inplace=True)
        curve["returns"] = curve["total"].pct_change()
        curve["equity_curve"] = (1.0 + curve["returns"]).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        if self.equity_curve is None:
            raise ValueError("Equity curve not created")

        total_return = self.equity_curve["equity_curve"].iloc[-1]
        returns = self.equity_curve["returns"]
        pnl = self.equity_curve["equity_curve"]

        sharpe = create_sharpe_ratio(returns, periods=252) # periods = 252*6.5*60
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)

        self.equity_curve["drawdown"] = drawdown
        self.equity_curve.to_csv("output/equity.csv")

        return [
            ("Total Return", f"{(total_return - 1.0) * 100:.2f}%"),
            ("Sharpe Ratio", f"{sharpe:.2f}"),
            ("Max Drawdown", f"{max_dd * 100:.2f}%"),
            ("Drawdown Duration", f"{dd_duration}"),
        ]


