import pandas_ta as ta


StrategyReal = ta.Strategy(
    name="Momo and Volatility",
    description="Ichimoku, RSI, MACD",
    ta=[
        {"kind": "ichimoku", "include_chikou": False},
        {"kind": "bop"},
        {"kind": "macd"}],
)


def strategy(df):
    """call from main, expects a return for entry and/or exit.
    this can either be BUY or SELL or NaN.
    """
    df.ta.strategy(StrategyReal)
    # ENTRY
    df['BOP_calc'] = 0
    df['BOP_14'] = 0
    df['BOP_14'] = df['BOP'].rolling(14).mean()
    df.loc[(df['BOP_14'] < 0), 'BOP_calc'] = -1
    df.loc[(df['BOP_14'] > 0), 'BOP_calc'] = 1
    df.loc[(df['BOP_calc'] == 1) & (df['BOP_calc'].shift(1) == -1), 'bop_entry'] = 'BUY'
    df.loc[(df['BOP_calc'] == -1) & (df['BOP_calc'].shift(1) == 1), 'bop_entry'] = 'SELL'

    df['macdh_calc'] = (df['MACDh_12_26_9']) >= 0
    df['macd_signal'] = df['macdh_calc'].shift(1) != df['macdh_calc']
    df.loc[(df['macdh_calc'] == False) & (df['macd_signal'] == True), f'macd_entry'] = 'SELL'
    df.loc[(df['macdh_calc'] == True) & (df['macd_signal'] == True), f'macd_entry'] = 'BUY'

    df.loc[(df['bop_entry'] == 'SELL') & (df['macd_entry'] == 'SELL'), '_entry'] = 'SELL'
    df.loc[(df['bop_entry'] == 'BUY') & (df['macd_entry'] == 'BUY'), '_entry'] = 'BUY'

    # EXIT
    df['calc_bool'] = (df['ITS_9'] - df['IKS_26']) >= 0
    df['ichi_signal'] = df['calc_bool'].shift(1) != df['calc_bool']  # TRUE where there is a cross
    df.loc[(df['calc_bool'] == True) & (df['ITS_9'] > df[['ISB_26', 'ISA_9']].max(axis=1)) & (
                df['ichi_signal'] == True), '_exit'] = 'BUY'
    df.loc[(df['calc_bool'] == False) & (df['ITS_9'] < df[['ISB_26', 'ISA_9']].min(axis=1)) & (
                df['ichi_signal'] == True), '_exit'] = 'SELL'

    return df.iloc[-1]['_entry'], df.iloc[-1]['_exit']

