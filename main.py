from db_checker import db_checker, trunc_db
import pandas as pd
import pandas_ta as ta
from os import environ
import time
from binance import ThreadedWebsocketManager
from binance.client import Client
from binance.enums import *
# 31.17 value of my usdt + btc


def btc_trade_history(msg):
    """ define how to process incoming WebSocket messages """
    if msg['e'] != 'error':
        open_order = client.get_open_orders(symbol='BTCUSDT')
        btc_price['error'] = False
        cleaned_msg = msg["k"]
        cleaned_msg["E"] = msg["E"]
        a = create_frame(cleaned_msg)
        next_close = db_checker('BTCUSDT_Calc').values[0][0]
        current_close = a['Close'].values[0]
        print(current_close, next_close)
        if not open_order:
            if next_close > current_close:  # IF WE PREDICT THAT THE NEXT CLOSE IS HIGHER THE CURRENT CLOSE
                if 1 - current_close / next_close > 0.005:  # IF THE DIFFERENCE BETWEEN THE TWO VALUES IS > 0.005
                    client.create_order(
                        symbol='BTCUSDT',
                        side=SIDE_BUY,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=0.0003,
                        price=str(current_close))
                    client.create_order(
                        symbol='BTCUSDT',
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=0.0003,
                        price=str("{:0.0{}f}".format(next_close, 0)))
                    print(f'created BUY order WITH PRICE {current_close}) SHOULD SELL AT {str("{:0.0{}f}".format(next_close, 0))}')
                else:
                    print('difference between next and current close is not profitable')
                    pass
            elif next_close <= current_close:   # IF WE PREDICT THAT THE NEXT CLOSE IS LOWER
                if 1 - next_close / current_close > 0.005:  # IF THE DIFFERENCE BETWEEN THE TWO VALUES IS > 0.005
                    client.create_order(
                        symbol='BTCUSDT',
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=0.0003,
                        price=str(current_close))
                    client.create_order(
                        symbol='BTCUSDT',
                        side=SIDE_BUY,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=0.0003,
                        price=str("{:0.0{}f}".format(next_close, 0)))
                    print(f'created SELL order WITH PRICE {current_close}) SHOULD BUY AT {str("{:0.0{}f}".format(next_close, 0))}')
                else:
                    print('difference between next and current close is not profitable')
                    pass

        elif open_order:
            # check if open order would make money, if yes make money. if not do nothing.
            if len(open_order) == 1:
                if abs(float(open_order[0]['price']) - next_close) > 200:
                    # CODE HERE TO CANCEL ORDER AND PLACE NEW ORDER WITH THE NEXT CLOSE
                    # THIS WAY WE HAVE MORE TRADES BUT WITH LESS PROFITABILITY PER TRADE (EVEN LOSS)
                    side = open_order[0]['side']
                    print('should cancel and create new order')
                else:
                    # DO NOTHING
                    print('leave it as it is ')
            else:
                print('multiple orders open.')
    else:
        btc_price['error'] = True
        print(msg['e'])


def create_frame(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:, ['E', 's', 'o', 'c', 'h', 'l', 'v']]
    df.columns = ['Time', 'Symbol', 'Open', 'Close', 'High', 'Low', 'Volume']
    df.Open = df.Open.astype(float)
    df.Close = df.Close.astype(float)
    df.High = df.High.astype(float)
    df.Low = df.Low.astype(float)
    df.Volume = df.Volume.astype(float)
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index(pd.DatetimeIndex(df["Time"]))
    return df


def main():
    # stream
    bsm = ThreadedWebsocketManager(environ.get("binance_key"), environ.get("binance_secret"))
    bsm.start()
    bsm.start_kline_socket(callback=btc_trade_history, symbol='BTCUSDT', interval='5m', )


btc_price = {'error': False}
client = Client(environ.get("binance_key"), environ.get("binance_secret"))

if __name__ == '__main__':
    main()

# get the last 200~ entries.
# run the  customstrategy on it and save it to db
# predict th next value
# start stream
# if stream ['Close'] is higher then the predicted value SELL else BUY
#  keep tracking the stream until the profit or stop loss is hit and execute it.
# close stream
# REPEAT
