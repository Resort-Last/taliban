from os import environ
from DBHandler import DBHandler
from binance.client import Client
from binance import ThreadedWebsocketManager


"""CHANGING HERE THE SYMBOL/INTERVAL."""
SYMBOL = 'BTCUSDT'
INTERVAL = '15m'
historical_kline_start = '5 day ago UTC'  # CHANGE THIS IF YOU CHANGE THE INTERVAL TO GET MORE / LESS HISTORICAL CANDLES
tp_mod = 0.01   # MODIFIER FOR THE STOP LOSS AND TAKE PROFIT PRICE
sl_mod = 0.05
leverage = 5    # FUTURES LEVERAGE 1x - 125x I THINK
quantity = 0.06    # AMOUNT OF COINS YOU WANT TO BUY
logged_user = "Lastresort"

"""binance client related data"""
db_obj = DBHandler(db=f'{SYMBOL}.db', table=f'{SYMBOL}_Futures')


def get_bsm():
    # bsm fix for stream
    client = Client(environ.get("binance_key"), environ.get("binance_secret"))
    bsm = ThreadedWebsocketManager(environ.get("binance_key"), environ.get("binance_secret"))
    return {'client': client, 'bsm': bsm}
