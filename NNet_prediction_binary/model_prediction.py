import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
import tensorflow as tf
from DBHandler import db_checker



WINDOW_SIZE = 5


def preprocess():
    df = db_checker("BTCUSDT")

    # drop nan values, time column, symbol, predict close: [-1]

    df = df.drop(['Time', 'Symbol'], axis=1)
    df = df.dropna(0)
    df = df.reindex(columns=['Open', 'High', 'Low', 'Volume', 'SMA_20',
           'SMA_50', 'BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0', 'BBB_20_2.0',
           'BBP_20_2.0', 'RSI_14', 'MACD_8_21_9', 'MACDh_8_21_9', 'MACDs_8_21_9',
           'VOLUME_SMA_20', 'Close'])

    column_scaler = {}
    for column in df.columns:
        scaler = RobustScaler()
        df[column] = scaler.fit_transform(np.expand_dims(df[column].values, axis=1))
        column_scaler[column] = scaler
    x_fut = df_to_x_y(df)
    next_close = next_value(column_scaler, x_fut)
    return next_close


def df_to_x_y(dataframe, window_size=WINDOW_SIZE):
    df_as_np = dataframe.to_numpy()
    x = []
    y = []
    for i in range(len(dataframe) - window_size):
        row = [r for r in df_as_np[i:i+window_size]]
        x.append(row)
        y.append(df_as_np[i+window_size][-1])
    x_future = [df_as_np[len(dataframe) - window_size: len(dataframe)]]
    return np.array(x_future)


def next_value(column_scaler, x_fut):
    model1 = tf.keras.models.load_model('./model-best.h5')
    next_close = column_scaler['Close'].inverse_transform(model1.predict(x_fut).reshape(-1, 1)).flatten()
    return next_close
