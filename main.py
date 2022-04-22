import pandas as pd
from binance.enums import *
import config
import time
from apply_strat import strategy
# 31.17 value of my usdt + btc

SYMBOL = config.SYMBOL
INTERVAL = config.INTERVAL
btc_price = {'error': False}
client = config.client
db_obj = config.db_obj


def main():
    while True:
        df = db_obj.query_main()
        df.set_index(pd.DatetimeIndex(df["Time"]), inplace=True)
        _entry, _exit = strategy(df)
        if not pd.isna(_entry) or not pd.isna(_exit):
            print(f'Price: {df.iloc[-1].Close} entry: {_entry} exit: {_exit}')
            # ha van entry/exit go to do client stuff.
        time.sleep(10)


if __name__ == '__main__':
    main()
