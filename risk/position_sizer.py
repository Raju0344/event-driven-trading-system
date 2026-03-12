class QuantityManager:
    def __init__(
        self,
        capital: float,
        risk_per_trade: float = 0.2,
        max_position_pct: float = 0.2
    ):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.max_position_pct = max_position_pct

    def calculate_quantity(self, price: float) -> int:
        """
        Fixed risk position sizing
        """
        risk_amount = self.capital * self.risk_per_trade
        qty = risk_amount // price

        max_qty = (self.capital * self.max_position_pct) // price
        return int(min(qty, max_qty))
