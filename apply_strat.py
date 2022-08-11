import pandas_ta as ta


StrategyOne = ta.Strategy(
    name="Momo and Volatility",
    description="Ichimoku, RSI, MACD",
    ta=[
        {"kind": "ichimoku", "include_chikou": False},
        {"kind": "bop"}]
)


def strategy(df):
    """call from main, expects a return for entry and/or exit.
    this can either be BUY or SELL or NaN.
    """
    df.ta.strategy(StrategyOne)
    # ENTRY
    df['BOP_calc'] = 0
    df['BOP_14'] = 0
    df['BOP_14'] = df['BOP'].rolling(14).mean()
    df.loc[(df['BOP_14'] < 0), 'BOP_calc'] = -1
    df.loc[(df['BOP_14'] > 0), 'BOP_calc'] = 1
    df.loc[(df['BOP_calc'] == 1) & (df['BOP_calc'].shift(1) == -1), '_entry'] = 'BUY'
    df.loc[(df['BOP_calc'] == -1) & (df['BOP_calc'].shift(1) == 1), '_entry'] = 'SELL'

    # EXIT
    df['calc_bool'] = (df['ITS_9'] - df['IKS_26']) >= 0
    df['ichi_signal'] = df['calc_bool'].shift(1) != df['calc_bool']  # TRUE where there is a cross
    df.loc[(df['calc_bool'] == True) & (df['ITS_9'] > df[['ISB_26', 'ISA_9']].max(axis=1)) & (
                df['ichi_signal'] == True), '_exit'] = 'BUY'
    df.loc[(df['calc_bool'] == False) & (df['ITS_9'] < df[['ISB_26', 'ISA_9']].min(axis=1)) & (
                df['ichi_signal'] == True), '_exit'] = 'SELL'

    return df.iloc[-1]['_entry'], df.iloc[-1]['_exit']

