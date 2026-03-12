# event.py

class Event:

    """
    Event is base class providing an interface for all subsequent (inherited )
    events, that will trigged futher events in the trading infrastructure.
    """
    pass


# 1. MarketEvent
class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with corresponding bars.
    """

    def __init__(self):
        """
        Initialised the MarketEvent
        """
        self.type = "MARKET"


# 2. SignalEvent
class SignalEvent(Event):

    """
    Handles the event of sending a Signal from a strategy object. 
    This is received by a protfolio object and acted upon.
    """
    def __init__(self, strategy_id, symbol, datetime, signal_type, strength):
        """
        Initialises the SignalEvent.

        Parameters:
        strategy_id - The unique identifier for the strategy that generate signal.

        symbol - The ticker symbol eg. 'GOOG'.
        datetime - The timestamp at which signal was generated .
        signal_type - "LONG" OR "SHORT"
        strength - An adjustment factor "suggestion" used to scale quantity at 
                         the portfolio level. Useful for pairs strategies. 
        
        """
        self.type = "SIGNAL"
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength


# 3. OrderEvent 
class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (eg. GOOG), a type (market or limit),
    quantity and a direction.
    """
    def __init__(self, symbol, order_type, quantity, direction, entry_exit):
        """
        Initialise the order type, setting whether it is a Market order ("MKT")
        or Limit order ("LMT"), has a quantity (integral) and its direction ("BUY" OR "SELL").

        Parameters:
        symbol : The instrument to trade
        order_type : "MKT" or "LMT" for market or limit.
        quantity : Non-negative integer for quantity.
        direction: "BUY" or "SELL" for long or short
        """

        self.type = "ORDER"
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction
        self.entry_exit = entry_exit

    def print_order(self):
        """
        Outputs the values within the order.
        """
        print("Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s"%
              (self.symbol, self.order_type, self.quantity, self.direction))


# 4. FillEvent
class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order as returned form a brokerage.
    Stores the quantity of an instrument actually filled and at what price.
    In addition stores the commission of the trade form the brokerage.
    """
    def __init__(self, timeindex, symbol, exchange, quantity, direction, fill_cost, commission=None):
        """
        Initialised the FillEvent object. Sets the symbol, exchange quantity, direction, cost of fill
        and an optional commission.

        IF commission is not provide, the fill object will calculated it based on the 
        trade size and Interactive Brokers fees.

        Parameters: 
        timeindex: The bar-resoution when the order was filled.
        symbol: The instrument which was filled.
        exchange: The exchange where the order was filled.
        quantity: The filled quantity
        direction: The direction of fill("BUY" OR "SELL")
        fill_cost: The holding value in dollars.
        commission: An option commission sent from IB
        
        """
        self.type = "FILL"
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange 
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        # Calculate commission
        if commission is None:
            self.commission = self.calculated_ib_commission()
        else:
            self.commission = commission

    
    def calculated_ib_commission(self):
        """
        Calculated the fees of trading based on an Interactive Brokers 
        fee structure for API , in USD

        This does not include exchange or ECN fees.

        """
        full_cost = 1.3
        if self.quantity <= 500:
            full_cost= max(1.3, 0.013*self.quantity)
        else: # Greater than 500
            full_cost= max(1.3, 0.008*self.quantity)
            return full_cost


