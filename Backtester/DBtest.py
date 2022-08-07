import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib
import pandas_ta as ta
import matplotlib.pyplot as plt
from Get_database import transform_database

con = sqlite3.connect('rawdata.db')
data = pd.read_sql_query('Select * from rawdata;', con)
x = transform_database(data, 15)
changing_indicator = data.ta.obv()
figure, axes = plt.subplots(1, 2)
data.plot(ax=axes[0])
changing_indicator.plot(ax=axes[1])
plt.show()
# for i in range (0, (len(shortdb))):
#     timelist=[]
#     openlist=[]
#     highlist=[]
#     lowlist=[]
#     closelist=[]
#     volumelist=[]
#     timelist.append(data["Time"][i])
#     openlist.append(data["Open"][i])
#     highlist.append(data["High"][i])
#     lowlist.append(data["Low"][i])
#     closelist.append(data["Close"][i])
#     volumelist.append(data["Volume"][i])

# def transform_database(interval):
#     candles = {
#         'Time': [],
#         'Open': [],
#         'High': [],
#         'Low': [],
#         'Close': [],
#         'Volume': [],
#         'Symbol': [],
#     }
#     i = 0
#     while i <= (len(shortdb) - interval):
#         sliceddb = shortdb.iloc[i: i+interval]
#         candles["Time"].append(sliceddb["Time"][i])
#         candles["Open"].append(sliceddb["Open"][i])
#         candles["High"].append(max(sliceddb["High"]))
#         candles["Low"].append(min(sliceddb["Low"]))
#         candles["Close"].append(sliceddb["Close"][i+(interval - 1)])
#         candles["Volume"].append(sum(sliceddb["Volume"]))
#         candles["Symbol"].append((sliceddb)["Symbol"][i])
#         i += interval
#     candle_dataframe = pd.DataFrame.from_dict(candles)
#     return(candle_dataframe)
#
# print(shortdb)
# print(transform_database(3))
# print(transform_database(5))
