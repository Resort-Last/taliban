import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import mean_absolute_error as mae
from sklearn.utils import shuffle
from db_checker import db_checker

WINDOW_SIZE = 5
BATCH_SIZE = 50
EPOCHS = 200

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


def df_to_x_y(dataframe, window_size=WINDOW_SIZE):
    df_as_np = df.to_numpy()
    x = []
    y = []
    for i in range(len(dataframe) - window_size):
        row = [r for r in df_as_np[i:i+window_size]]
        x.append(row)
        y.append(df_as_np[i+window_size][-1])
    x_future = [df_as_np[len(dataframe) - window_size: len(dataframe)]]
    return np.array(x), np.array(y), np.array(x_future)


x, y, x_fut = df_to_x_y(df)
print(x.shape, y.shape)
q, p = int(len(df) * 0.8), int(len(df) * 0.9)
x_train = x[:q]
y_train = y[:q]
x_val = x[q:p]
y_val = y[q:p]
x_test = x[p:]
y_test = y[p:]

x_train, y_train = shuffle(x_train, y_train)

early_stopping = tf.keras.callbacks.EarlyStopping(patience=20, monitor='val_mean_absolute_error', verbose=1)

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_mean_absolute_error', min_lr=0.00001,
                                                 patience=20, mode='min',
                                                 verbose=1)

model_checkpoint = tf.keras.callbacks.ModelCheckpoint(monitor='val_mean_absolute_error',
                                                      filepath='model-best.h5',
                                                      save_best_only=True)

callbacks = [
    early_stopping,
    reduce_lr,
    model_checkpoint
]


def create_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv1D(64, input_shape=(WINDOW_SIZE, x.shape[2]), kernel_size=3, activation='relu'),
        tf.keras.layers.Conv1D(32, kernel_size=3, activation='relu'),
        tf.keras.layers.GlobalAveragePooling1D(),
        #tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, return_sequences=True)),
        #tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32, return_sequences=True)),
        #tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32, return_sequences=True)),
        #tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(16)),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation='linear')
    ])
    model.compile(loss=tf.keras.losses.MeanAbsoluteError(),
                  optimizer=tf.keras.optimizers.Adam(),
                  metrics=[tf.keras.metrics.MeanAbsoluteError()])
    model.fit(x_train, y_train, validation_data=(x_val, y_val), batch_size=BATCH_SIZE, epochs=EPOCHS, verbose=1, callbacks=[callbacks])
    return model


def plot_predictions2(model, X, y, start=0, end=200):
    predictions = model.predict(X)
    predictions = column_scaler['Close'].inverse_transform(predictions.reshape(-1, 1)).flatten()
    y = column_scaler['Close'].inverse_transform(y.reshape(-1, 1)).flatten()
    plt.plot(predictions, label='pred', color='red')
    plt.plot(y, label='actual', color='blue')
    print(f'mse:{mse(y, predictions)}, mae:{mae(y, predictions)}')
    new_df = pd.DataFrame({'prediction': predictions, 'actuals': y})
    print(new_df)
    plt.title(mse(y, predictions))
    plt.legend()
    plt.grid(True)
    plt.show()


def next_value():
    model1 = tf.keras.models.load_model('./model-best.h5')
    next_close = column_scaler['Close'].inverse_transform(model1.predict(x_fut).reshape(-1, 1)).flatten()
    print(f"next close: {model1.predict(x_fut)}/{next_close}")
    return next_close


#model1 = create_model()
#plot_predictions2(model1, x_test, y_test)

