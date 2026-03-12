from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from utils import ConfigJson, get_logger

cwd = os.chdir("/home/raju/MAIN_DIRECTORY/zerodha")
config = ConfigJson("config/config.json")
config_symbol_list = ConfigJson("config/config_symbols.json")
logger = get_logger("Historical Data")

#generate trading session
kite = KiteConnect(config.get("api_key")) # main object
kite.set_access_token(config.get("access_token"))

#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE") # list the all instrument of "NSE"
instrument_df = pd.DataFrame(instrument_dump)

engine = create_engine(
                f"mysql+pymysql://{config.get("USER")}:{quote_plus(config.get("RAW_PASSWORD"))}@{config.get("HOST")}/{config.get("DB")}"
                )

# def insert_symbol_to_database():
#     symbols = []
#     now = datetime.datetime.now()
#     for row in instrument_df.itertuples(index=False):
#         symbols.append((1, row.tradingsymbol, "EQ", row.name, row.name, "INR", now, now))

    
#     sql = text("""
#     INSERT INTO symbol_table
#     (exchange_id, ticker, instrument, name, sector, currency, created_date, last_updated_date)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#     """)

#     with engine.begin() as conn:
#         conn.exec_driver_sql(sql.text, symbols)

from sqlalchemy import text
from sqlalchemy.engine import Engine


def obtain_list_of_db_tickers():
    """
    Obtain (id, ticker) from DB using SQLAlchemy Core.
    """
    sql = text("SELECT id, ticker FROM symbol_table WHERE id>51")

    with engine.connect() as conn:
        result = conn.execute(sql)
        data = result.fetchall()

    return data

def instruments_token(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1

#list =[]
# ---------------- DOWNLOADING THE MARKET DATA ----------------
def get_daily_historic_data(
    ticker, 
    last_updated_date,
    interval="5minute"
):
    """
    Download daily OHLCV data from Yahoo Finance using yfinance.
    """
    try:
        """extracts historical data and outputs in the form of dataframe"""
        instrument_token = instruments_token(instrument_df,ticker)
        df = pd.DataFrame(kite.historical_data(instrument_token,last_updated_date, dt.date.today(),interval))
        df.set_index("date",inplace=True)

        if df.empty:
            return []

        prices = []
        for date, row in df.iterrows():
            prices.append((
                date.to_pydatetime(),
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
                int(row["volume"])
            ))
        #list.append(ticker)

        return prices

    except Exception as e:
        logger.error(f"Zerodha download failed for {ticker}: {e}")
        return []

import datetime
from sqlalchemy import text
from sqlalchemy.engine import Engine


def insert_daily_data_into_db(
    data_vendor_id,
    symbol_id,
    daily_data,
):
    """
    Insert daily price data into MySQL using SQLAlchemy.
    """
    if not daily_data:
        return

    now = dt.datetime.now()

    # list of tuples (same as your original code)
    insert_rows = [
        (
            data_vendor_id,
            symbol_id,
            d[0],      # price_date      # last_updated_date
            d[1],      # open
            d[2],      # high
            d[3],      # low
            d[4],      # close
            d[5],      # volume
            now, 
            now
        )
        for d in daily_data
    ]

    sql = """
    INSERT INTO price_table (
        data_vendor_id,
        symbol_id,
        price_time,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        created_date,
        last_updated_date
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        last_updated_date = VALUES(last_updated_date),
        open_price = VALUES(open_price),
        high_price = VALUES(high_price),
        low_price = VALUES(low_price),
        close_price = VALUES(close_price),
        volume = VALUES(volume)
    """

    # transactional + auto-commit
    with engine.begin() as conn:
        conn.exec_driver_sql(sql, insert_rows)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    tickers = obtain_list_of_db_tickers() # Data feching from the Database
    total = len(tickers)
    DATA_VENDOR_ID = 2

    logger.info(f"Found {total} symbols")
    last_updated_date = dt.datetime.fromisoformat(config.get("last_updated_date"))
    time_frame = config.get("time_frame")
    now = dt.datetime.now()

    for i, (symbol_id, ticker) in enumerate(tickers, start=1):
        logger.info(f"[{i}/{total}] Downloading {ticker}")

        data = get_daily_historic_data(ticker, last_updated_date, time_frame) # Download the Data from the yfinance
        insert_daily_data_into_db(DATA_VENDOR_ID, symbol_id, data) # inserting the data into the Databse

    logger.info("Zerodha Finance price ingestion completed")
    config.set("last_updated_date", now.isoformat()) # Update the on the config.json
    #config_symbol_list.set("symbol_list", list)
    