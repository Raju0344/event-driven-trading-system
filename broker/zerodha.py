from datetime import datetime
from kiteconnect import KiteTicker




class InstrumentMapper:
    def __init__(self, instrument_df):
        self.df = instrument_df

    def symbols_to_tokens(self, symbols):
        return [
            int(self.df[self.df.tradingsymbol == s]
                .instrument_token.values[0])
            for s in symbols
        ]

    def symbol_to_token(self, symbol):
        try:
            return int(
                self.df[self.df.tradingsymbol == symbol]
                .instrument_token.values[0]
            )
        except IndexError:
            return -1
    
    def tokens_to_symbols(self, tokens):
        return [
            self.df[self.df.instrument_token == s]
                .tradingsymbol.values[0]
            for s in tokens
        ]



class KiteTickRecorder:
    def __init__(self, api_key, access_token, tokens, mapper, tick_db, live):
        self.tokens = tokens
        self.mapper = mapper
        self.tick_db = tick_db
        self.live = live
        self.state = {"last_minute": None}


        self.kws = KiteTicker(api_key, access_token)
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect

    def on_connect(self, ws, response):
        ws.subscribe(self.tokens)
        ws.set_mode(ws.MODE_FULL, self.tokens)
        print("Connected & subscribed", self.mapper.tokens_to_symbols(self.tokens))

    def on_ticks(self, ws, ticks):
        self.tick_db.insert_ticks(ticks) 
        #print(ticks)
        now = datetime.now()
        if now.minute % 5 == 0 and now.second >= 5:
            # prevent multiple triggers in same minute
            if self.state["last_minute"] != now.minute:
                self.state["last_minute"] = now.minute
                self.live._run_live()

    def start(self):
        self.kws.connect()


