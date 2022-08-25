import pandas as pd
from os import environ
import config
import time
from apply_strat import strategy
from binance.client import Client
from datetime import datetime
from Notification import send_discord_message
# 31.17 value of my usdt + btc

SYMBOL = config.SYMBOL
INTERVAL = config.INTERVAL
btc_price = {'error': False}
db_obj = config.db_obj
sl_mod = config.sl_mod
tp_mod = config.tp_mod
quantity = config.quantity


def reverser(pos_type):
    if pos_type == 'BUY':
        return 'SELL'
    elif pos_type == 'SELL':
        return 'BUY'
    else:
        return 'BOTH'


def binance_con(price, pos_entry, pos_exit):
    client = Client(environ.get("binance_key"), environ.get("binance_secret"))
    client.futures_change_leverage(symbol=SYMBOL, leverage=config.leverage)
    open_orders = client.futures_get_open_orders(symbol=SYMBOL)
    print(len(open_orders))
    for item in client.futures_position_information():
        if item['symbol'] == SYMBOL:
            if float(item['positionAmt']) == 0.00 and len(open_orders) == 0:
                if not pd.isna(pos_entry):
                    client.futures_create_order(
                        symbol=SYMBOL,
                        type='LIMIT',
                        timeInForce='GTC',  # Can be changed - see link to API doc below
                        price=float(round(price, 0)),  # The price at which you wish to buy/sell, float
                        side=pos_entry,  # Direction ('BUY' / 'SELL'), string
                        quantity=quantity,  # Number of coins you wish to buy / sell, float
                    )
                    if pos_entry == 'BUY':
                        tp_price = float(round(price * (1+tp_mod), 0))
                        sl_price = float(round(price * (1-sl_mod), 0))
                    elif pos_entry == 'SELL':
                        tp_price = float(round(price * (1-tp_mod), 0))
                        sl_price = float(round(price * (1+sl_mod), 0))
                    else:
                        tp_price, sl_price = price
                        print('HUGE ISSUES HERE. THIS SHOULD NEVER HAPPEN')
                    client.futures_create_order(
                        symbol=SYMBOL,
                        type='TAKE_PROFIT',
                        price=tp_price,
                        quantity=quantity,
                        stopPrice=tp_price,
                        side=reverser(pos_entry)
                    )
                    client.futures_create_order(
                        symbol=SYMBOL,
                        type='STOP',
                        price=sl_price,
                        quantity=quantity,
                        stopPrice=sl_price,
                        side=reverser(pos_entry)
                    )
                    print(f'Created order: {pos_entry} @ {price}')
                    send_discord_message(f'Created new order for {config.logged_user} price: {pos_entry} @ {price}')
            elif float(item['positionAmt']) != 0.00 and len(open_orders) == 2:
                print('want to close position')
                if not pd.isna(pos_exit):
                    print(pos_exit, client.futures_get_open_orders(symbol=SYMBOL)[0]["side"])
                    if pos_exit == client.futures_get_open_orders(symbol=SYMBOL)[0]["side"]:
                        client.futures_create_order(
                            symbol=SYMBOL,
                            type='LIMIT',
                            timeInForce='GTC',  # Can be changed - see link to API doc below
                            price=float(round(price, 0)),  # The price at which you wish to buy/sell, float
                            side=pos_exit,  # Direction ('BUY' / 'SELL'), string
                            quantity=quantity,  # Number of coins you wish to buy / sell, float
                        )
                        print('close this position')
                        send_discord_message(f'Trying to close position for {config.logged_user} price: {pos_exit} @ {price}')
            elif float(item['positionAmt']) == 0.00 and len(open_orders) > 0:  # ha csak TP SL marad.
                print('trying to close the TP SL')
                client.futures_cancel_all_open_orders(symbol=SYMBOL)

    """https://binance-docs.github.io/apidocs/futures/en/#new-order-trade"""


def main():
    while True:
        try:
            df = db_obj.query_main()
            df.set_index(pd.DatetimeIndex(df["Time"]), inplace=True)
            _entry, _exit = strategy(df)
            with open("heartbeat_log.txt", 'w+') as txtfile:
                txtfile.write(df.iloc[-1]['Time'])
            if not pd.isna(_entry) or not pd.isna(_exit):
                if not pd.isna(_entry) and not pd.isna(_exit):
                    if _entry != _exit:
                        pass
                    elif _entry == _exit:
                        binance_con(df.iloc[-1].Close, _entry, _exit)
                else:
                    binance_con(df.iloc[-1].Close, _entry, _exit)
        except pd.io.sql.DatabaseError as e:
            print(f"{datetime.now()}....\n{e}\n")
        time.sleep(10)

if __name__ == '__main__':
    main()
