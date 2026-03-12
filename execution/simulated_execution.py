import datetime
from typing import Optional

from .base_execution import ExecutionHandler
from core import FillEvent, OrderEvent
from utils import get_logger

logger = get_logger("FILL EVENT")


class SimulatedExecutionHandler(ExecutionHandler):
    """
    Simulated execution handler.

    Instantly fills all orders at market price with:
    - No latency
    - No slippage
    - No partial fills

    Useful for backtesting strategies.
    """

    def __init__(self, events, kite= None):
        """
        Parameters
        ----------
        events : queue.Queue
            Event queue used by the backtesting engine.
        """
        self.events = events

    def execute_order(self, event: OrderEvent) -> None:
        """
        Convert OrderEvent into FillEvent immediately.
        """
        if event.type != "ORDER":
            return
        symbol = event.symbol
        direction = event.direction
        quantity = event.quantity

        fill_event = FillEvent(
            timeindex=datetime.datetime.now(),
            symbol=symbol,
            exchange="SIMULATED",
            quantity=quantity,
            direction=direction,
            fill_cost=None,
            commission=1.3
        )
        
        logger.info(f"FILLED ORDER | {symbol} | {direction} | {quantity}")

        self.events.put(fill_event)
