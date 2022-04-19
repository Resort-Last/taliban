from binance.client import Client
from os import environ
import pandas as pd
import pandas_ta as ta
from NNet_prediction_binary import model_prediction
from db_checker import trunc_db
import sqlite3
import time


CustomStrategy = ta.Strategy(
    name="Momo and Volatility",
    description="SMA 20,50, BBANDS, RSI, MACD and Volume SMA 20",
    ta=[
        {"kind": "sma", "length": 20},
        {"kind": "sma", "length": 50},
        {"kind": "bbands", "length": 20},
        {"kind": "rsi"},
        {"kind": "macd", "fast": 8, "slow": 21},
        {"kind": "sma", "close": "volume", "length": 20, "prefix": "VOLUME"},
    ]
)


def create_historical_frame(klines):
    df = pd.DataFrame(klines,
                      columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_Time', 'Quote_assets_volume',
                               'No_of_trades', 'taker_buy_vol', 'taker_buy_ass', 'ignore'])
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df = df.drop(['Close_Time', 'Quote_assets_volume', 'No_of_trades', 'taker_buy_vol', 'taker_buy_ass', 'ignore'],
                 axis=1)
    df.Open = df.Open.astype(float)
    df.Close = df.Close.astype(float)
    df.High = df.High.astype(float)
    df.Low = df.Low.astype(float)
    df.Volume = df.Volume.astype(float)
    df['Symbol'] = 'BTCUSDT'
    df = df.reindex(columns=['Time', 'Symbol', 'Open', 'Close', 'High', 'Low', 'Volume'])
    df.set_index(pd.DatetimeIndex(df["Time"]))
    df.ta.strategy(CustomStrategy)

    conn = sqlite3.connect('../BTCUSDT.db')
    df.to_sql('BTCUSDT', conn, if_exists='append', index=False)
    conn.close()


def fill_db():
    client = Client(environ.get("binance_key"), environ.get("binance_secret"))
    a = client.get_historical_klines('BTCUSDT', interval='5m', start_str='1 day ago UTC')
    a = a[:-1]
    create_historical_frame(a)
    next_close = model_prediction.preprocess()
    print(next_close)
    df = pd.DataFrame(next_close, columns=['next_close'])
    trunc_db("BTCUSDT")
    conn = sqlite3.connect('../BTCUSDT_Calc.db')
    df.to_sql('BTCUSDT_Calc', conn, if_exists='replace', index=False)
    conn.close()


if __name__ == '__main__':
    while True:
        fill_db()
        print('filled DB, sleeping now for 5')
        time.sleep(300)

