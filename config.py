from os import environ
from DBHandler import DBHandler
from binance.client import Client
from binance import ThreadedWebsocketManager


"""CHANGING HERE THE SYMBOL/INTERVAL."""
SYMBOL = 'BTCUSDT'
INTERVAL = '1m'
historical_kline_start = '1 day ago UTC'  # CHANGE THIS IF YOU CHANGE THE INTERVAL TO GET MORE / LESS HISTORICAL CANDLES
db_obj = DBHandler(db=f'{SYMBOL}.db', table=f'{SYMBOL}_Futures')
client = Client(environ.get("binance_key"), environ.get("binance_secret"))
bsm = ThreadedWebsocketManager(environ.get("binance_key"), environ.get("binance_secret"))
