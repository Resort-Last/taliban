from os import environ
import pandas as pd
from binance.client import Client
import sqlite3


def btc_trade_history(msg):
    """ define how to process incoming WebSocket messages """
    if msg['e'] != 'error':
        btc_price['error'] = False
        cleaned_msg = msg["k"]
        cleaned_msg["E"] = msg["E"]
        a = create_frame(cleaned_msg)
        conn = sqlite3.connect('BTCUSDT.db')
        a.to_sql('BTCUSDT', conn, if_exists='append', index=False)
        conn.close()
    else:
        btc_price['error'] = True


def get_minute_data(symbol, interval, lookback):
    frame = pd.DataFrame(Client.futures_historical_klines(symbol, interval, lookback + 'min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def create_frame():
    client = Client(environ.get("binance_key"), environ.get("binance_secret"))
    a = client.get_historical_klines('BTCUSDT', interval='15m', start_str='30 day ago UTC')
    a = a[:-1]
    df = pd.DataFrame(a,
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
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index(pd.DatetimeIndex(df["Time"]), inplace=True)
    return df


# client = Client(environ.get("binance_key"), environ.get("binance_secret"))

# bsm = ThreadedWebsocketManager(environ.get("binance_key"), environ.get("binance_secret"))
# bsm.start()
# bsm.start_kline_socket(callback=btc_trade_history, symbol='BTCUSDT')
# btc_price = {'error': False}


