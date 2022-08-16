import pandas_ta as ta


StrategyReal = ta.Strategy(
    name="Momo and Volatility",
    description="Ichimoku, RSI, MACD",
    ta=[
        {"kind": "ichimoku", "include_chikou": False},
        {"kind": "bbands", "std": 2.5},
        {"kind": "ema", "length": 100}],
)


def strategy(df):
    """call from main, expects a return for entry and/or exit.
    this can either be BUY or SELL or NaN.
    """
    df.ta.strategy(StrategyReal)
    # ENTRY
    df.loc[(df['BBU_5_2.5'] < df['High']), '_entry'] = 'SELL'
    df.loc[(df['BBL_5_2.5'] > df['Low']), '_entry'] = 'BUY'

    # EXIT
    df['calc_bool'] = (df['ITS_9'] - df['IKS_26']) >= 0
    df['ichi_signal'] = df['calc_bool'].shift(1) != df['calc_bool']  # TRUE where there is a cross
    df.loc[(df['calc_bool'] == True) & (df['ITS_9'] > df[['ISB_26', 'ISA_9']].max(axis=1)) & (
                df['ichi_signal'] == True), '_exit'] = 'BUY'
    df.loc[(df['calc_bool'] == False) & (df['ITS_9'] < df[['ISB_26', 'ISA_9']].min(axis=1)) & (
                df['ichi_signal'] == True), '_exit'] = 'SELL'

    return df.iloc[-1]['_entry'], df.iloc[-1]['_exit']

