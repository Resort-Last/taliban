import pandas as pd
from get_historical_klines import historical_futures_klines
import config


SYMBOL = config.SYMBOL
INTERVAL = config.INTERVAL
btc_price = {'error': False}
client = config.get_bsm()['client']
bsm = config.get_bsm()['bsm']
db_obj = config.db_obj


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
        cleaned_msg["s"] = msg["ps"]    # symbol (in futures it is perpetual symbol | ps for some reason)
        a = create_frame(cleaned_msg)
        db_obj.replace_last_entry(a)
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
    df.set_index(pd.DatetimeIndex(df["Time"]), inplace=False)
    return df


def main(symbol, interval):
    historical_futures_klines(client=client, symbol=symbol, interval=interval, db_obj=db_obj)
    # stream
    bsm.start()
    bsm.start_kline_futures_socket(callback=btc_futures_handler, symbol=symbol, interval=interval)


if __name__ == '__main__':
    main(symbol=SYMBOL, interval=INTERVAL)
