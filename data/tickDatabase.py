import pandas as pd
import sqlite3

from utils import get_logger

logger = get_logger("Market Event")

class TickDatabase:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.db.cursor()

    def create_tables(self, tokens):
        for token in tokens:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS TOKEN{token} (
                    ts DATETIME PRIMARY KEY,
                    price REAL,
                    volume INTEGER
                )
            """)
        self.db.commit()

    def insert_ticks(self, ticks):
        for tick in ticks:
            try:
                table = f"TOKEN{tick['instrument_token']}"
                values = (
                    tick["exchange_timestamp"],
                    tick["last_price"],
                    tick["last_traded_quantity"]
                )
                self.cursor.execute(
                    f"INSERT INTO {table} (ts, price, volume) VALUES (?, ?, ?)",
                    values
                )
            except sqlite3.IntegrityError:
                #logger.error("Unable to insert the data into datebase")
                pass
        self.db.commit()

    def close(self):
        self.db.close()

    def fetch_ticks_since(self, token, days=1):
        query = f"""
            SELECT ts, price, volume
            FROM TOKEN{token}
            WHERE ts >= datetime('now', '-{days} day')
            ORDER BY ts
        """
        return pd.read_sql(query, self.db, parse_dates=["ts"])
