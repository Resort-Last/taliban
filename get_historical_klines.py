import pandas as pd
from config import historical_kline_start


def historical_futures_klines(client, symbol, interval, db_obj):
    a = client.futures_historical_klines(symbol, interval=interval, start_str=historical_kline_start)
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
    db_obj.trunc_db(sure=True)
    db_obj.append_db(df)
    print(f'filled DB with historical klines len data: {len(df)}')

