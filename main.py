import pandas as pd
from binance.enums import *
from os import environ
import config
import time
from apply_strat import strategy
from binance.client import Client
# 31.17 value of my usdt + btc

SYMBOL = config.SYMBOL
INTERVAL = config.INTERVAL
btc_price = {'error': False}
db_obj = config.db_obj


def reverser(pos_type):
    if pos_type == 'BUY':
        return 'SELL'
    elif pos_type == 'SELL':
        return 'BUY'
    else:
        return 'BOTH'


def binance_con(price, pos_entry, pos_exit):
    client = Client(environ.get("binance_key"), environ.get("binance_secret"))
    client.futures_change_leverage(symbol=SYMBOL, leverage=3)
    profit_mod = 0.05
    for item in config.client.futures_position_information():
        if item['symbol'] == SYMBOL:
            if float(item['positionAmt']) == 0.00:
                if not pd.isna(pos_entry):
                    client.futures_create_order(
                        symbol=SYMBOL,
                        type='LIMIT',
                        timeInForce='GTC',  # Can be changed - see link to API doc below
                        price=float(round(price, 0)),  # The price at which you wish to buy/sell, float
                        side=pos_entry,  # Direction ('BUY' / 'SELL'), string
                        quantity=0.001,  # Number of coins you wish to buy / sell, float
                    )
                    if pos_entry == 'BUY':
                        tp_price = float(round(price * (1+profit_mod), 0))
                        sl_price = float(round(price * (1-profit_mod), 0))
                    elif pos_entry == 'SELL':
                        tp_price = float(round(price * (1-profit_mod), 0))
                        sl_price = float(round(price * (1+profit_mod), 0))
                    else:
                        tp_price, sl_price = price
                        print('HUGE ISSUES HERE. THIS SHOULD NEVER HAPPEN')
                    client.futures_create_order(
                        symbol=SYMBOL,
                        type='TAKE_PROFIT',
                        price=tp_price,
                        quantity=0.001,
                        stopPrice=tp_price,
                        side=reverser(pos_entry)
                    )
                    client.futures_create_order(
                        symbol=SYMBOL,
                        type='STOP',
                        price=sl_price,
                        quantity=0.001,
                        stopPrice=sl_price,
                        side=reverser(pos_entry)
                    )
                    print(f'Created order: {pos_entry} @ {price}')
            elif float(item['positionAmt']) > 0.00:
                if not pd.isna(pos_exit):
                    side = reverser(item['positionSide'])
                    client.futures_create_order(
                        symbol=SYMBOL,
                        type='LIMIT',
                        timeInForce='GTC',  # Can be changed - see link to API doc below
                        price=float(round(price, 0)),  # The price at which you wish to buy/sell, float
                        side=side,  # Direction ('BUY' / 'SELL'), string
                        quantity=0.001,  # Number of coins you wish to buy / sell, float
                    )
                    print('sell this position')

    """https://binance-docs.github.io/apidocs/futures/en/#new-order-trade"""


def main():
    while True:
        df = db_obj.query_main()
        df.set_index(pd.DatetimeIndex(df["Time"]), inplace=True)
        _entry, _exit = strategy(df)
        if not pd.isna(_entry) or not pd.isna(_exit):
            print(f'Price: {df.iloc[-1].Close} entry: {_entry} exit: {_exit}')
            binance_con(df.iloc[-1].Close, _entry, _exit)
            # ha van entry/exit go to do client stuff.
        time.sleep(10)


if __name__ == '__main__':
    main()
