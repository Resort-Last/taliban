from db_checker import db_checker, trunc_db
import pandas as pd
import pandas_ta as ta
from os import environ
from binance import ThreadedWebsocketManager
from binance.client import Client
from binance.enums import *
# 31.17 value of my usdt + btc

SYMBOL = 'BTCUSDT'
INTERVAL = '1m'
btc_price = {'error': False}
client = Client(environ.get("binance_key"), environ.get("binance_secret"))


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


def btc_futures_handler(msg):
    """ define how to process incoming WebSocket messages
        {
    "e":"continuous_kline",   // Event type
    "E":1607443058651,        // Event time
    "ps":"BTCUSDT",           // Pair
    "ct":"PERPETUAL"          // Contract type
    "k":{
        "t":1607443020000,      // Kline start time
        "T":1607443079999,      // Kline close time
        "i":"1m",               // Interval
        "f":116467658886,       // First trade ID
        "L":116468012423,       // Last trade ID
        "o":"18787.00",         // Open price
        "c":"18804.04",         // Close price
        "h":"18804.04",         // High price
        "l":"18786.54",         // Low price
        "v":"197.664",          // volume
        "n": 543,               // Number of trades
        "x":false,              // Is this kline closed?
        "q":"3715253.19494",    // Quote asset volume
        "V":"184.769",          // Taker buy volume
        "Q":"3472925.84746",    //Taker buy quote asset volume
        "B":"0"                 // Ignore
    }
}
    """
    if msg['e'] != 'error':
        btc_price['error'] = False
        cleaned_msg = msg["k"]
        cleaned_msg["s"] = msg["ps"]    # symbol (in futures it is perpetual symbol / ps for some reason)
        a = create_frame(cleaned_msg)
        if bool(cleaned_msg["x"]):
            print('Closed, new entry should be created in DB')
            print(a)
        else:
            print('not closed')

    else:
        btc_price['error'] = True


def create_frame(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:, ['t', 's', 'o', 'c', 'h', 'l', 'v']]
    df.columns = ['Time', 'Symbol', 'Open', 'Close', 'High', 'Low', 'Volume']
    df.Open = df.Open.astype(float)
    df.Close = df.Close.astype(float)
    df.High = df.High.astype(float)
    df.Low = df.Low.astype(float)
    df.Volume = df.Volume.astype(float)
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index(pd.DatetimeIndex(df["Time"]))
    return df


def main(symbol, interval):
    # have to fill up DB with the historic k-lines
    # stream
    bsm = ThreadedWebsocketManager(environ.get("binance_key"), environ.get("binance_secret"))
    bsm.start()
    bsm.start_kline_futures_socket(callback=btc_futures_handler, symbol=symbol, interval=interval)


if __name__ == '__main__':
    main(symbol=SYMBOL, interval=INTERVAL)
