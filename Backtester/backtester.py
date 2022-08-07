from Get_database import transform_database
from DBHandler import DBHandler
import pandas as pd
import pandas_ta as ta


db_obj = DBHandler(db=f'rawdata.db', table=f'rawdata')
StrategyOne = ta.Strategy(
    name="Momo and Volatility",
    description="Ichimoku, RSI, MACD",
    ta=[
        {"kind": "ichimoku", "include_chikou": False},
        {"kind": "rsi"}]
)


class BackTester:
    """TODO:Calculate profits"""

    def __init__(self, strategy, db, interval, start_date, end_date):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.dataframe = transform_database(db, interval)
        self.processed_df = self.apply_strategy()
        print(self.processed_df)

    def apply_strategy(self):
        self.dataframe.ta.strategy(self.strategy)
        df = self.dataframe.dropna(0)

        # ta. number 1
        df['calc_bool'] = (df['ITS_9'] - df['IKS_26']) >= 0
        df['ichi_signal'] = df['calc_bool'].shift(1) != df['calc_bool']  # TRUE where there is a cross
        df.loc[(df['calc_bool'] == True) & (df['ITS_9'] > df[['ISB_26', 'ISA_9']].max(axis=1)) & (
                    df['ichi_signal'] == True), f'{self.strategy.ta[0]["kind"]}_entry'] = 'BUY'
        df.loc[(df['calc_bool'] == False) & (df['ITS_9'] < df[['ISB_26', 'ISA_9']].min(axis=1)) & (
                    df['ichi_signal'] == True), f'{self.strategy.ta[0]["kind"]}_entry'] = 'SELL'

        signal_one = df.dropna(subset=[f'{self.strategy.ta[0]["kind"]}_entry'])

        # ta. number 2
        df['RSI_calc'] = 0
        df.loc[(df['RSI_14'] < 20), 'RSI_calc'] = -1
        df.loc[(df['RSI_14'] > 80), 'RSI_calc'] = 1
        df.loc[(df['RSI_calc'] == 0) & (df['RSI_calc'].shift(1) == -1), f'{self.strategy.ta[1]["kind"]}_exit'] = 'BUY'
        df.loc[(df['RSI_calc'] == 0) & (df['RSI_calc'].shift(1) == 1), f'{self.strategy.ta[1]["kind"]}_exit'] = 'SELL'
        signal_two = df.dropna(subset=[f'{self.strategy.ta[1]["kind"]}_exit'])

        # combined list without the first signal

        signal = signal_one.append(signal_two)
        signal = signal.sort_values(by='Time')
        signal = signal[['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol', f'{self.strategy.ta[0]["kind"]}_entry', f'{self.strategy.ta[1]["kind"]}_exit']]

        # apply time constraints
        if self.start_date:
            signal = signal[(signal['Time'] >= self.start_date)]
        if self.end_date:
            signal = signal[(signal['Time'] <= self.end_date)]

        return signal

    def calculate_profit(self):
        pass


if __name__ == '__main__':
    dingdong = BackTester(strategy=StrategyOne, db=db_obj, interval=15, start_date='2022-01-01', end_date=None)
