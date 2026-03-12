from __future__ import annotations

from abc import ABC, abstractmethod

from core import FillEvent, OrderEvent

class ExecutionHandler(ABC):
    """
    Abstract base class for execution handlers.

    Converts OrderEvent objects into FillEvent objects.
    Can be subclassed for simulated or live broker execution.
    """

    @abstractmethod
    def execute_order(self, event: OrderEvent) -> None:
        """
        Execute an OrderEvent and place a FillEvent onto the event queue.

        Parameters
        ----------
        event : OrderEvent
            The order to be executed.
        """
        raise NotImplementedError("execute_order() must be implemented")
