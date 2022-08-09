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

    def __init__(self, strategy, db, interval, start_date, end_date, signals):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.dataframe = transform_database(db, interval)
        self.dataframe.ta.strategy(self.strategy)
        self.df = self.dataframe.dropna(0)
        self.signals = signals
        self.signal_list = []
        for signal in self.signals:
            self.signal_list.append(self.ta_lib_calculations(signal))
        self.processed_df = self.apply_strategy()

        print(self.processed_df)

    def apply_strategy(self):
        signal = pd.DataFrame().append(self.signal_list)
        signal = signal.sort_values(by='Time')
        if self.start_date:
            signal = signal[(signal['Time'] >= self.start_date)]
        if self.end_date:
            signal = signal[(signal['Time'] <= self.end_date)]
        return signal

    def calculate_profit(self):
        pass

    # Ta.lib goes here
    def ta_lib_calculations(self, strat):
        if strat == 'ichimoku':
            self.df['calc_bool'] = (self.df['ITS_9'] - self.df['IKS_26']) >= 0
            self.df['ichi_signal'] = self.df['calc_bool'].shift(1) != self.df['calc_bool']  # TRUE where there is a cross
            self.df.loc[(self.df['calc_bool'] == True) & (self.df['ITS_9'] > self.df[['ISB_26', 'ISA_9']].max(axis=1)) & (
                        self.df['ichi_signal'] == True), f'{strat}_entry'] = 'BUY'
            self.df.loc[(self.df['calc_bool'] == False) & (self.df['ITS_9'] < self.df[['ISB_26', 'ISA_9']].min(axis=1)) & (
                        self.df['ichi_signal'] == True), f'{strat}_entry'] = 'SELL'
            signal = self.df.dropna(subset=[f'{strat}_entry'])
            signal = signal[['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol', f'{strat}_entry']]
            return signal

        elif strat == 'rsi':
            self.df['RSI_calc'] = 0
            self.df.loc[(self.df['RSI_14'] < 20), 'RSI_calc'] = -1
            self.df.loc[(self.df['RSI_14'] > 80), 'RSI_calc'] = 1
            self.df.loc[(self.df['RSI_calc'] == 0) & (self.df['RSI_calc'].shift(1) == -1), f'{strat}_exit'] = 'BUY'
            self.df.loc[(self.df['RSI_calc'] == 0) & (self.df['RSI_calc'].shift(1) == 1), f'{strat}_exit'] = 'SELL'
            signal = self.df.dropna(subset=[f'{strat}_exit'])
            signal = signal[['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol', f'{strat}_exit']]
            return signal

        elif strat == 'whatever':
            # do stuff
            # return signal
            pass


if __name__ == '__main__':
    dingdong = BackTester(strategy=StrategyOne,
                          db=db_obj,
                          interval=15,
                          start_date='2022-01-01',
                          end_date=None,
                          signals=['ichimoku', 'rsi'])
