from DBHandler import DBHandler
import pandas as pd
import pandas_ta as ta


# db_obj = DBHandler('BTCUSDT.db', 'BTCUSDT_Futures')
# df = db_obj.query_main()

StrategyOne = ta.Strategy(
    name="Momo and Volatility",
    description="Ichimoku, RSI, MACD",
    ta=[
        {"kind": "ichimoku", "include_chikou": False},
        {"kind": "rsi"}]
)


def strategy(df):
    """call from main, expects a return for entry and/or exit.
    this can either be BUY or SELL or NaN.
    """
    df.ta.strategy(StrategyOne)
    df['calc_bool'] = (df['ITS_9'] - df['IKS_26']) >= 0
    df['ichi_signal'] = df['calc_bool'].shift(1) != df['calc_bool']  # TRUE where there is a cross
    df.loc[(df['calc_bool'] == True) & (df['ITS_9'] > df[['ISB_26', 'ISA_9']].max(axis=1)) & (df['ichi_signal'] == True), 'ichi_entry'] = 'BUY'
    df.loc[(df['calc_bool'] == False) & (df['ITS_9'] < df[['ISB_26', 'ISA_9']].min(axis=1)) & (df['ichi_signal']==True), 'ichi_entry'] = 'SELL'
    df['RSI_calc'] = 0
    df.loc[(df['RSI_14'] < 20), 'RSI_calc'] = -1
    df.loc[(df['RSI_14'] > 80), 'RSI_calc'] = 1
    df.loc[(df['RSI_calc'] == 0) & (df['RSI_calc'].shift(1) == -1), 'RSI_exit'] = 'BUY'
    df.loc[(df['RSI_calc'] == 0) & (df['RSI_calc'].shift(1) == 1), 'RSI_exit'] = 'SELL'
    return df.iloc[-1]['ichi_entry'], df.iloc[-1]['RSI_exit']

