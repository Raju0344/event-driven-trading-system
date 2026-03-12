#main.py
import datetime
import os

from data import HistoricMySQLDataHandler, LiveZerodhaDataHandler, TickDatabase
from execution import SimulatedExecutionHandler, ZerodhaExecutionHandler
from portfolio import Portfolio
from core import Engine
from broker import InstrumentMapper, KiteTickRecorder
from utils import ConfigJson, MarketClock
from plot import plot_all

from strategy import strategy_dict


from kiteconnect import KiteConnect, KiteTicker
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd
import sqlite3
import threading

#list = {"ID1":HistoricMySQLDataHandler, "ID2":ZerodhaExecutionHandler}
config = ConfigJson("config/config.json")
config_symbol_list = ConfigJson("config/config_symbols.json")
mode = config.get("mode") 
sequential_processing = config.get("sequential_processing")

def main():
    os.chdir(config.get("working_directory"))

    heartbeat = config.get("heartbeat")
    symbol_list = config.get("symbol_list")
    #symbol_list = config_symbol_list.get("symbol_list")
    
   
    if mode == "backtesting":
        start_date = datetime.datetime.fromisoformat(config.get("start_date"))
        initial_capital = config.get("initial_capital")

        db_engine = create_engine(
            f"mysql+pymysql://{config.get("USER")}:{quote_plus(config.get("RAW_PASSWORD"))}@{config.get("HOST")}/{config.get("DB")}"
            )

         # sequential/batch
        if sequential_processing == True:
            for s_name, strategy in strategy_dict.items():
                symbol_list = config_symbol_list.get("symbol_list")
                df = pd.DataFrame()
                for symbol in symbol_list:
                    backtest = Engine(
                    symbol_list=[symbol],
                    initial_capital=initial_capital,
                    heartbeat=heartbeat,
                    start_date=start_date,
                    data_handler_class=HistoricMySQLDataHandler,
                    execution_handler_class=SimulatedExecutionHandler,
                    portfolio_class=Portfolio,
                    strategy_class=strategy,
                    db_engine=db_engine
                    )
                    backtest.simulate_trading()
                    stats, events = backtest._output_performance()
                    df[symbol] = {stats[0][0]:stats[0][1],stats[1][0]:stats[1][1],stats[2][0]:stats[2][1], stats[3][0]:stats[3][1], events[0][0]:events[0][1],events[1][0]:events[1][1],events[2][0]:events[2][1]}
                df.to_csv(f"output/{s_name}.csv")
            
            for s_name in strategy_dict:
                df = pd.read_csv(f"output/{s_name}.csv")
                df = df.T
                df.columns = df.iloc[0]
                df = df.iloc[1:]
                df["Total Return"] = df["Total Return"].str.rstrip("%").astype(float)
                df["Max Drawdown"] = df["Max Drawdown"].str.rstrip("%").astype(float)
                df = df.sort_values(by=["Total Return", "Sharpe Ratio", "Max Drawdown", "Drawdown Duration"], ascending=[False, False, True, True])
                print(f"---------------------------------------- {s_name} ----------------------")
                print(df.head(15))
            
        else:
            backtest = Engine(
                symbol_list=symbol_list,
                initial_capital=initial_capital,
                heartbeat=heartbeat,
                start_date=start_date,
                data_handler_class=HistoricMySQLDataHandler,
                execution_handler_class=SimulatedExecutionHandler,
                portfolio_class=Portfolio,
                strategy_class=strategy_dict["mrp"],
                db_engine=db_engine
                )
            backtest.simulate_trading()
            backtest._output_performance()
    else:
        start_date = datetime.datetime.now()

        kite = KiteConnect(api_key=config.get("api_key"))
        kite.set_access_token(access_token=config.get("access_token"))
        initial_capital = kite.margins()["equity"]["net"]

        mapper = InstrumentMapper(pd.DataFrame(kite.instruments(config.get("exchange"))))
        tokens = mapper.symbols_to_tokens(symbol_list)

        db_engine = TickDatabase("data/ticks.db")
        db_engine.create_tables(tokens)

        live = Engine(
            symbol_list=symbol_list,
            initial_capital=initial_capital,
            heartbeat=heartbeat,
            start_date=start_date,
            data_handler_class=LiveZerodhaDataHandler,
            execution_handler_class=ZerodhaExecutionHandler if mode == "live" else SimulatedExecutionHandler,
            portfolio_class=Portfolio,
            strategy_class=strategy_dict["mrp"],
            db_engine=db_engine,
            mapper=mapper,
            kit = kite
            )
        
        recorder = KiteTickRecorder(
            api_key=kite.api_key,
            access_token=kite.access_token,
            tokens=tokens,
            mapper = mapper,
            tick_db=db_engine,
            live = live
            )

        MarketClock.wait_for_open()

        recorder.start()

        while True:
            MarketClock.exit_at_close()
    

if __name__ == "__main__":
    if mode == "backtesting":
        main()
        if sequential_processing == False:
            #plot_all()
            pass
    else:
        main()









