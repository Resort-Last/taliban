import sqlite3
import pandas as pd


def db_checker(db):
    """returns the values of the DB as a pd.df"""
    conn = sqlite3.connect(f'{db}.db')
    a = f'SELECT * FROM {db}'
    df = pd.read_sql_query(a
                           , conn)
    conn.close()
    return df


#print(db_checker("BTCUSDT"))


def trunc_db(db):
    conn = sqlite3.connect(f'{db}.db')
    conn.execute(f'DROP TABLE {db}')


#trunc_db("BTCUSDT")
"""
[{'symbol': 'BTCUSDT'
     , 'orderId': 3100878217
     , 'orderListId': -1
     , 'clientOrderId': 'and_15dffdea50b44a84a639277265a781a2'
     , 'price': '11318.00000000'
     , 'origQty': '0.01536300'
     , 'executedQty': '0.01536300'
     , 'cummulativeQuoteQty': '173.87843400'
     , 'status': 'FILLED'
     , 'timeInForce': 'GTC'
     , 'type': 'LIMIT'
     , 'side': 'SELL'
     , 'stopPrice': '0.00000000'
     , 'icebergQty': '0.00000000'
     , 'time': 1599113712705
     , 'updateTime': 1599117901096
     , 'isWorking': True
     , 'origQuoteOrderQty': '0.00000000'}
    ,

 {'symbol': 'BTCUSDT'
     , 'orderId': 3859187768
     , 'orderListId': -1
     , 'clientOrderId': 'web_62ac3b87e7414e098e483fb3a5c7d70d'
     , 'price': '18070.16000000'
     , 'origQty': '0.05566600'
     , 'executedQty': '0.05566600'
     , 'cummulativeQuoteQty': '1005.85957030'
     , 'status': 'FILLED'
     , 'timeInForce': 'GTC'
     , 'type': 'LIMIT'
     , 'side': 'BUY'
     , 'stopPrice': '0.00000000'
     , 'icebergQty': '0.00000000'
     , 'time': 1607509394655
     , 'updateTime': 1607509394655
     , 'isWorking': True
     , 'origQuoteOrderQty': '0.00000000'}
    ,

 {'symbol': 'BTCUSDT'
     , 'orderId': 3891539934
     , 'orderListId': -1
     , 'clientOrderId': 'and_007d595b72dd4ab8beef7c34431e931f'
     , 'price': '18998.91000000'
     , 'origQty': '0.05562800'
     , 'executedQty': '0.05562800'
     , 'cummulativeQuoteQty': '1056.87136548'
     , 'status': 'FILLED'
     , 'timeInForce': 'GTC'
     , 'type': 'LIMIT'
     , 'side': 'SELL'
     , 'stopPrice': '0.00000000'
     , 'icebergQty': '0.00000000'
     , 'time': 1607842856387
     , 'updateTime': 1607842863646
     , 'isWorking': True
     , 'origQuoteOrderQty': '0.00000000'}
    ,

 {'symbol': 'BTCUSDT'
     , 'orderId': 5339686630
     , 'orderListId': -1
     , 'clientOrderId': 'web_457a830cd1bb4b2db9102bb96d138570'
     , 'price': '53655.65000000'
     , 'origQty': '0.00020400'
     , 'executedQty': '0.00020400'
     , 'cummulativeQuoteQty': '10.94575260'
     , 'status': 'FILLED'
     , 'timeInForce': 'GTC'
     , 'type': 'LIMIT'
     , 'side': 'BUY'
     , 'stopPrice': '0.00000000'
     , 'icebergQty': '0.00000000'
     , 'time': 1616621903830
     , 'updateTime': 1616621904149
     , 'isWorking': True
     , 'origQuoteOrderQty': '0.00000000'}]
"""