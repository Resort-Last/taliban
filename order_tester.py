import config
from binance.enums import *


SYMBOL = config.SYMBOL
INTERVAL = config.INTERVAL
btc_price = {'error': False}
db_obj = config.db_obj

pos_entry = 'SELL'
price = 39700


def open_pos():
    for item in config.client.futures_position_information():
        if item['symbol'] == SYMBOL:
            print(item)
            if float(item['positionAmt']) > 0.00:
                print('sell this position')
            else:
                print('no position open')


def create_order():
    config.client.futures_create_order(
        symbol=SYMBOL,
        type="STOP",
        price=41000,  # The price at which you wish to buy/sell, float
        stopPrice=40995,
        side='BUY',  # Direction ('BUY' / 'SELL'), string
        quantity=0.001,  # Number of coins you wish to buy / sell, float
    )


