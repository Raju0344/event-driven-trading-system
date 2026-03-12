# Execution Handler
import datetime
from typing import Optional

from .base_execution import ExecutionHandler
from core import FillEvent, OrderEvent
from utils import get_logger

logger = get_logger("FILL EVENT")

class ZerodhaExecutionHandler(ExecutionHandler):
    """
    Simulated execution handler.

    Instantly fills all orders at market price with:
    - No latency
    - No slippage
    - No partial fills

    Useful for backtesting strategies.
    """

    def __init__(self, events, kite):
        """
        Parameters
        ----------
        events : queue.Queue
            Event queue used by the backtesting engine.
        """
        self.events = events
        self.kite = kite

    def placeMarketOrder(self, symbol, buy_sell, quantity):    
        # Place an intraday market order on NSE {product -> MIS(Margin Intraday )}
        if buy_sell == "BUY":
            t_type=self.kite.TRANSACTION_TYPE_BUY
        elif buy_sell == "SELL":
            t_type=self.kite.TRANSACTION_TYPE_SELL
        response = self.kite.place_order(tradingsymbol=symbol,
                        exchange=self.kite.EXCHANGE_NSE,
                        transaction_type=t_type,
                        quantity=quantity,
                        order_type=self.kite.ORDER_TYPE_MARKET,
                        product=self.kite.PRODUCT_MIS,
                        variety=self.kite.VARIETY_REGULAR
                        )
        return response   
    
    def exitMarketOrder(self, symbol, buy_sell, quantity):
        positions = self.kite.positions()
        p = positions["net"][0]
        if p["quantity"] != 0:
            if buy_sell == "BUY":
                t_type=self.kite.TRANSACTION_TYPE_BUY
            elif buy_sell == "SELL":
                t_type=self.kite.TRANSACTION_TYPE_SELL

            response = self.kite.place_order(
                        variety=self.kite.VARIETY_REGULAR,
                        exchange=self.kite.EXCHANGE_NSE,
                        tradingsymbol=symbol,
                        transaction_type=t_type,
                        quantity=quantity,
                        product=self.kite.PRODUCT_MIS,
                        order_type=self.kite.ORDER_TYPE_MARKET
                    )
            return response

    def execute_order(self, event: OrderEvent) -> None:
        """
        Convert OrderEvent into FillEvent immediately.
        """
        if event.type != "ORDER":
            return
        
        now = datetime.datetime.now()

        symbol = event.symbol
        quantity = event.quantity
        direction = event.direction
        entry_exit = event.entry_exit

        fill_event = FillEvent(
                timeindex=now,
                symbol=symbol,
                exchange="ZERODHA",
                quantity=quantity,
                direction=direction,
                fill_cost=None,
                commission=1.3
            )
        
        if entry_exit == "ENTRY":
            try:
                response = self.placeMarketOrder(symbol, direction, quantity)
            except Exception as e:
                logger.info(f"[ERROR] Order failed | {symbol} | {direction} | {quantity} | {e}")
                response = None
            if isinstance(response, str):
                logger.info(f"FILLED ORDER | {symbol} | {direction} | {quantity}")
                self.events.put(fill_event)
        
        if entry_exit == "EXIT":
            try:
                response = self.exitMarketOrder(symbol, direction, quantity)
            except Exception as e:
                logger.info(f"[ERROR] Order failed | {symbol} | {direction} | {quantity} | {e}")
                response = None
            if isinstance(response, str):
                logger.info(f"FILLED ORDER | {symbol} | {direction} | {quantity}")
                self.events.put(fill_event)




