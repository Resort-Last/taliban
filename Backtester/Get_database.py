from binance.client import Client
from os import environ
import pandas as pd
import pandas_ta as ta
from DBHandler import DBHandler
import sqlite3
from Notification import send_discord_message
"""
USAGE: Set the symbol to the coin you would like, and create a {symbol}rawdata file. Run the raw_data function (once).
Once you have the rawdata you can run the transform_database function using parameters of your liking from 
backtester.py
"""
api_key = environ.get("binance_key")
api_secret = environ.get('binance_secret')
symbol = "BTCUSDT"
client = Client(api_key, api_secret)
db_obj = DBHandler(db=f'{symbol}rawdata.db', table=f'rawdata')
con = sqlite3.connect(f'{symbol}rawdata.db')
historical_data = pd.read_sql_query(f'Select * from rawdata;', con)


def raw_data(symbol, database):
    a = client.futures_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "4 Aug, 2021")
    a = a[:-1]
    df = pd.DataFrame(a,
                      columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_Time', 'Quote_assets_volume',
                               'No_of_trades', 'taker_buy_vol', 'taker_buy_ass', 'ignore'])
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df = df.drop(['Close_Time', 'Quote_assets_volume', 'No_of_trades', 'taker_buy_vol', 'taker_buy_ass', 'ignore'],
                 axis=1)
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index(pd.DatetimeIndex(df["Time"]), inplace=False)
    df['Symbol'] = symbol
    df.Open = df.Open.astype(float)
    df.Close = df.Close.astype(float)
    df.High = df.High.astype(float)
    df.Low = df.Low.astype(float)
    df.Volume = df.Volume.astype(float)
    database.trunc_db(sure=True)
    database.append_db(df)

# raw_data(symbol, db_obj)
# takes a long time, dont run often


def append_database(symbol, database):
    lastentry = str(historical_data["Time"][len(historical_data["Time"])-1])
    a = client.futures_historical_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, start_str=lastentry)
    a = a[:-1]
    df = pd.DataFrame(a,
                      columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_Time', 'Quote_assets_volume',
                               'No_of_trades', 'taker_buy_vol', 'taker_buy_ass', 'ignore'])
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df = df.drop(['Close_Time', 'Quote_assets_volume', 'No_of_trades', 'taker_buy_vol', 'taker_buy_ass', 'ignore'],
                 axis=1)
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index(pd.DatetimeIndex(df["Time"]), inplace=False)
    df['Symbol'] = symbol
    df.Open = df.Open.astype(float)
    df.Close = df.Close.astype(float)
    df.High = df.High.astype(float)
    df.Low = df.Low.astype(float)
    df.Volume = df.Volume.astype(float)
    database.append_db(df[1:])


def transform_database(database, interval):
    append_database("BTCUSDT", database)
    historical_data = pd.read_sql_query(f'Select * from rawdata;', con)
    candles = {
        'Time': [],
        'Open': [],
        'High': [],
        'Low': [],
        'Close': [],
        'Volume': [],
        'Symbol': [],
    }
    i = 0
    while i <= (len(historical_data) - interval):
        sliced_db = historical_data.iloc[i: i + interval]
        candles["Time"].append(sliced_db["Time"][i])
        candles["Open"].append(sliced_db["Open"][i])
        candles["High"].append(max(sliced_db["High"]))
        candles["Low"].append(min(sliced_db["Low"]))
        candles["Close"].append(sliced_db["Close"][i + (interval - 1)])
        candles["Volume"].append(sum(sliced_db["Volume"]))
        candles["Symbol"].append(sliced_db["Symbol"][i])
        i += interval
    candle_dataframe = pd.DataFrame.from_dict(candles)
    return candle_dataframe
