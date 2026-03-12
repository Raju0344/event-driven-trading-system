import time
import sys
import datetime


class MarketClock:
    MARKET_OPEN = (9, 15)
    MARKET_CLOSE = (15, 21)

    @staticmethod
    def wait_for_open():
        while True:
            now = datetime.datetime.now()
            if (now.hour, now.minute) >= MarketClock.MARKET_OPEN:
                return
            time.sleep(5)

    @staticmethod
    def exit_at_close():
        now = datetime.datetime.now()
        if (now.hour, now.minute) >= MarketClock.MARKET_CLOSE:
            sys.exit()
