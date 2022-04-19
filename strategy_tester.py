import pandas as pd
import pandas_ta as ta
from binance_con import create_frame
from matplotlib import pyplot as plt
import pickle

StrategyOne = ta.Strategy(
    name="Momo and Volatility",
    description="Ichimoku, RSI, MACD",
    ta=[
        {"kind": "ichimoku", "include_chikou": False},
        {"kind": "rsi"},
        {"kind": "macd", "fast": 9, "slow": 26},
        {"kind": "ema", "length": 100}]
)


def backtester(df):
    signal = df.loc[
        (df['RSI_exit'] == 'SELL') | (df['RSI_exit'] == 'BUY') | (df['ichi_entry'] == 'BUY') | (
                df['ichi_entry'] == 'SELL')]
    signal = signal[['Close', 'ichi_entry', 'RSI_exit']]
    signal = signal.iloc[1:, :]
    trades = pd.DataFrame(columns={'Type', 'Open', 'Close'})
    for index, i in enumerate(signal.values):
        if i[1] == 'BUY':
            for j in signal.values[index:]:
                if j[2] == 'SELL':
                    trades = trades.append({'Type': 'LONG', 'Open': i[0], 'Close': j[0]}, ignore_index=True)
                    break
        if i[1] == 'SELL':
            for j in signal.values[index:]:
                if j[2] == 'BUY':
                    trades = trades.append({'Type': 'SHORT', 'Open': i[0], 'Close': j[0]}, ignore_index=True)
                    break
    trades.loc[(trades['Type'] == 'LONG'), 'outcome'] = trades['Close'] - trades['Open']
    trades.loc[(trades['Type'] == 'SHORT'), 'outcome'] = trades['Open'] - trades['Close']
    print('asd')


if __name__ == '__main__':
    # TODO: RSI exit where it changes from below 30 to above / 70 to below.
    # df = create_frame()
    with open('data/historical_data.pkl', 'rb') as f:
        df = pickle.load(f)
    df.ta.strategy(StrategyOne)
    df = df.dropna(0)
    df['calc_bool'] = (df['ITS_9'] - df['IKS_26']) >= 0
    df['ichi_signal'] = df['calc_bool'].shift(1) != df['calc_bool']  # TRUE where there is a cross
    df.loc[(df['calc_bool'] == True) & (df['ITS_9'] > df[['ISB_26', 'ISA_9']].max(axis=1)) & (df['ichi_signal'] == True), 'ichi_entry'] = 'BUY'
    df.loc[(df['calc_bool'] == False) & (df['ITS_9'] < df[['ISB_26', 'ISA_9']].min(axis=1)) & (df['ichi_signal']==True), 'ichi_entry'] = 'SELL'
    df['RSI_calc'] = 0
    df.loc[(df['RSI_14'] < 20), 'RSI_calc'] = -1
    df.loc[(df['RSI_14'] > 80), 'RSI_calc'] = 1
    df.loc[(df['RSI_calc'] == 0) & (df['RSI_calc'].shift(1) == -1), 'RSI_exit'] = 'BUY'
    df.loc[(df['RSI_calc'] == 0) & (df['RSI_calc'].shift(1) == 1), 'RSI_exit'] = 'SELL'
    backtester(df)


    print(df.columns)




# Random comment here

""" ICHIMOKU
    looking for ITS_9 to cross IKS_26 where ITS_9 > max(ISA_9, ISB_26)

    df['calc_bool'] = (df['ITS_9'] - df['IKS_26'])>= 0 - TRUE = UPTREND, FALSE = DOWNTREND
    df['cloud_pos'] = df['ITS_9'] > df[['ISB_26', 'ISA_9']].max(axis=1)  -- TRUE = ABOVE CLOUD, FALSE = BELOW CLOUD
    df['signal'] = df['calc_bool'].shift(1) != df['calc_bool'] # TRUE where this is a cross 
    
    if df signal true, check cloud_pos if down or uptrend + check calc_bool if down or uptrend if all match buy
    df2 = df.loc[(df['signal'] == True) & (df['calc_bool'] == df['cloud_pos'])]  
    
    MACD 
    check for MACDh_9_26_9(histogram) change in boolean value (+ long, - short) + check whether price is below EMA_100 or above.
    
    test_df['macdh_calc'] = (test_df['MACDh_9_26_9']) >= 0
    test_df['macd_signal'] = test_df['macdh_calc'].shift(1) != test_df['macdh_calc']
    test_df.loc[(test_df['macdh_calc'] == False) & (test_df['macd_signal'] == True) & (test_df['EMA_100'] > test_df['Close']), 'macd_entry'] = 'SELL'
    test_df.loc[(test_df['macdh_calc'] == True) & (test_df['macd_signal'] == True) & (test_df['EMA_100'] < test_df['Close']), 'macd_entry'] = 'BUY'
    
    test_df.loc[(test_df['calc_bool'] == True) & (test_df['cloud_pos'] == True) & (test_df['signal'] == True), 'entry'] = 'BUY'
    test_df.loc[(test_df['calc_bool'] == False) & (test_df['cloud_pos'] == False) & (test_df['signal'] == True), 'entry'] = 'SELL'
    
    RSI
    Should move between -1 0 1. 0-30, 30-70, 70-100.
    If it changes from the prev value TO 0, signal.
    
    test_df['RSI_calc'] = 0 
    test_df.loc[(test_df['RSI_14'] < 30), 'RSI_calc'] = -1
    test_df.loc[(test_df['RSI_14'] > 70 ), 'RSI_calc'] = 1 
    test_df.loc[(test_df['RSI_calc'] == 0) & (test_df['RSI_calc'].shift(1) == -1), 'RSI_exit'] = 'BUY'
    test_df.loc[(test_df['RSI_calc'] == 0) & (test_df['RSI_calc'].shift(1) == 1), 'RSI_exit'] = 'SELL'
    
"""
