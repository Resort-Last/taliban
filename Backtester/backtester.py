from Get_database import transform_database
from DBHandler import DBHandler
import pandas as pd
import pandas_ta as ta
from functools import reduce
from datetime import datetime
import pickle

db_obj = DBHandler(db=f'rawdata.db', table=f'rawdata')
StrategyOne = ta.Strategy(
    name="Momo and Volatility",
    description="Ichimoku, RSI, MACD",
    ta=[
        {"kind": "ichimoku", "include_chikou": False},
        {"kind": "bop"},
        {"kind": "macd"},
        {"kind": "ema", "length": 100},
        {"kind": "bbands", "std": 2.5}]
)


def ultra_looper(signals):
    pairs = []
    temp_pair = []
    final_pairs = []
    for i in signals:
        for k in signals:
            temp_pair.append(sorted([i, k]))
    for item in temp_pair:
        if item not in pairs:
            pairs.append(item)
    temp_pair.clear()
    for i in pairs:
        for k in pairs:
            temp_pair.append(sorted([i, k]))
    for item in temp_pair:
        if item not in final_pairs:
            final_pairs.append(item)
    return final_pairs


class BackTester:

    def __init__(self, strategy, db, interval, start_date, end_date, signals, tp, sl):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.dataframe = transform_database(db, interval)
        self.dataframe.ta.strategy(self.strategy)
        self.tp = tp
        self.sl = sl
        self.df = self.dataframe.dropna(0)
        self.signals = signals
        self.signal_list = []
        for signal in self.signals:
            self.signal_list.append(self.ta_lib_calculations(signal))
        self.processed_df = self.apply_strategy()
        self.calculate_profit(signals, interval)

    def apply_strategy(self):
        signal = reduce(lambda left, right: pd.merge(left, right, how='outer'), self.signal_list)
        signal = signal.sort_values(by='Time')
        if self.start_date:
            signal = signal[(signal['Time'] >= self.start_date)]
        if self.end_date:
            signal = signal[(signal['Time'] <= self.end_date)]
        return signal

    def calculate_profit(self, signals, interval):
        """ TODO: should have lookback(variable) -- TO BE REVISED."""
        col_list = []
        trades_dict = {}
        for col in self.processed_df.columns:
            col_list.append(col)
        for signal in ultra_looper(self.signals):
            _entry, _exit = signal[0], signal[1]
            last_time = pd.to_datetime('1990-09-09 09:00:00')

            trades = pd.DataFrame(columns={'Type', 'Open', 'Close', 'Time', 'Timedelta', 'TS', 'TP_SL'})
            for ind, i in enumerate(self.processed_df.values):
                if pd.to_datetime(self.processed_df.iloc[ind]['Time']) < last_time:
                    continue
                if i[col_list.index(_entry[0])] == 'BUY' and i[col_list.index(_entry[1])] == 'BUY':
                    take_profit = i[4] + (i[4] * self.tp)  # Close + Close * TP
                    stop_loss = i[4] - (i[4] * self.sl)  # Close - Close * TP
                    for j in self.processed_df.values[ind:]:
                        if j[col_list.index(_exit[0])] == 'SELL' and j[col_list.index(_exit[1])] == 'SELL':
                            trades = trades.append({'Type': 'LONG',
                                                    'Open': i[4],
                                                    'Close': j[4],
                                                    'Time': i[0],
                                                    'Timedelta': (datetime.strptime(j[0], "%Y-%m-%d %H:%M:%S")
                                                                  - datetime.strptime(i[0], "%Y-%m-%d %H:%M:%S")),
                                                    'TP_SL': False}, ignore_index=True)
                            last_time = pd.to_datetime(j[0])
                            break
                        elif j[3] <= stop_loss:  # High > tp, Low < SL
                            trades = trades.append({'Type': 'LONG',
                                                    'Open': i[4],
                                                    'Close': stop_loss,
                                                    'Time': i[0],
                                                    'Timedelta': (datetime.strptime(j[0], "%Y-%m-%d %H:%M:%S")
                                                                  - datetime.strptime(i[0], "%Y-%m-%d %H:%M:%S")),
                                                    'TP_SL': 'SL'}, ignore_index=True)
                            last_time = pd.to_datetime(j[0])
                            break
                        elif j[2] >= take_profit:  # High > tp, Low < SL
                            trades = trades.append({'Type': 'LONG',
                                                    'Open': i[4],
                                                    'Close': take_profit,
                                                    'Time': i[0],
                                                    'Timedelta': (datetime.strptime(j[0], "%Y-%m-%d %H:%M:%S")
                                                                  - datetime.strptime(i[0], "%Y-%m-%d %H:%M:%S")),
                                                    'TP_SL': 'TP'}, ignore_index=True)
                            last_time = pd.to_datetime(j[0])
                            break
                if i[col_list.index(_entry[0])] == 'SELL' and i[col_list.index(_entry[1])] == 'SELL':
                    take_profit = i[4] - (i[4] * self.tp)  # Close - Close * TP
                    stop_loss = i[4] + (i[4] * self.sl)  # Close + Close * SL
                    for j in self.processed_df.values[ind:]:
                        if j[col_list.index(_exit[0])] == 'BUY' and j[col_list.index(_exit[1])] == 'BUY':
                            trades = trades.append({'Type': 'SHORT',
                                                    'Open': i[4],
                                                    'Close': j[4],
                                                    'Time': i[0],
                                                    'Timedelta': (datetime.strptime(j[0], "%Y-%m-%d %H:%M:%S")
                                                                  - datetime.strptime(i[0], "%Y-%m-%d %H:%M:%S")),
                                                    'TP_SL': False}, ignore_index=True)
                            last_time = pd.to_datetime(j[0])
                            break
                        elif j[2] >= stop_loss:  # LOW < tp, High > SL
                            trades = trades.append({'Type': 'SHORT',
                                                    'Open': i[4],
                                                    'Close': stop_loss,
                                                    'Time': i[0],
                                                    'Timedelta': (datetime.strptime(j[0], "%Y-%m-%d %H:%M:%S")
                                                                  - datetime.strptime(i[0], "%Y-%m-%d %H:%M:%S")),
                                                    'TP_SL': 'SL'}, ignore_index=True)
                            last_time = pd.to_datetime(j[0])
                            break
                        elif j[3] <= take_profit:  # LOW < tp, High > SL
                            trades = trades.append({'Type': 'SHORT',
                                                    'Open': i[4],
                                                    'Close': take_profit,
                                                    'Time': i[0],
                                                    'Timedelta': (datetime.strptime(j[0], "%Y-%m-%d %H:%M:%S")
                                                                  - datetime.strptime(i[0], "%Y-%m-%d %H:%M:%S")),
                                                    'TP_SL': 'TP'}, ignore_index=True)
                            last_time = pd.to_datetime(j[0])
                            break
            trades.loc[(trades['Type'] == 'LONG'), 'outcome'] = trades['Close'] - trades['Open']
            trades.loc[(trades['Type'] == 'SHORT'), 'outcome'] = trades['Open'] - trades['Close']

            print(f"profit with entry: {_entry} exit: {_exit}\t{trades['outcome'].sum()}")
            print(f"Stats: with entry: {_entry} exit: {_exit}\n")
            print(f"""All No.:{len(trades)}\tprofit:{trades['outcome'].sum()}\n""")
            print(f"""LONG No.: {len(trades.query('Type == "LONG"'))}\t
                     profit:{trades.query('Type == "LONG"')['outcome'].sum()}\t
                     max:{trades.query('Type == "LONG"')['outcome'].max()} \t
                     min:{trades.query('Type == "LONG"')['outcome'].min()}\n""")
            print(f"""SHORT No.: {len(trades.query('Type == "SHORT"'))}\t
                     profit:{trades.query('Type == "SHORT"')['outcome'].sum()}\t
                     max:{trades.query('Type == "SHORT"')['outcome'].max()}\t
                     min:{trades.query('Type == "SHORT"')['outcome'].min()}\n""")
            print(f"""TP_SL No.: {len(trades.query('TP_SL != False'))}\t""")
            print('-' * 30)
            trades_dict[f'{signal[0][0]},{signal[0][1]}_{signal[1][0]},{signal[1][1]}'] = trades
        filename = ''
        for item in signals:
            filename += f'{item}_'
        filename += f'{interval}.pkl'
        with open(f'results\\{filename}', 'wb') as f:
            pickle.dump(trades_dict, f)

    # Ta.lib goes here
    def ta_lib_calculations(self, strat):
        if strat == 'ichimoku':
            self.df['calc_bool'] = (self.df['ITS_9'] - self.df['IKS_26']) >= 0
            self.df['ichi_signal'] = self.df['calc_bool'].shift(1) != self.df[
                'calc_bool']  # TRUE where there is a cross
            self.df.loc[
                (self.df['calc_bool'] == True) & (self.df['ITS_9'] > self.df[['ISB_26', 'ISA_9']].max(axis=1)) & (
                        self.df['ichi_signal'] == True), f'{strat}'] = 'BUY'
            self.df.loc[
                (self.df['calc_bool'] == False) & (self.df['ITS_9'] < self.df[['ISB_26', 'ISA_9']].min(axis=1)) & (
                        self.df['ichi_signal'] == True), f'{strat}'] = 'SELL'
            signal = self.df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol', f'{strat}']]
            return signal

        elif strat == 'rsi':
            self.df['RSI_calc'] = 0
            self.df.loc[(self.df['RSI_14'] < 30), 'RSI_calc'] = -1
            self.df.loc[(self.df['RSI_14'] > 70), 'RSI_calc'] = 1
            self.df.loc[(self.df['RSI_calc'] == 0) & (self.df['RSI_calc'].shift(1) == -1), f'{strat}'] = 'BUY'
            self.df.loc[(self.df['RSI_calc'] == 0) & (self.df['RSI_calc'].shift(1) == 1), f'{strat}'] = 'SELL'
            signal = self.df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol', f'{strat}']]
            return signal

        elif strat == 'macd':
            self.df['macdh_calc'] = (self.df['MACDh_12_26_9']) >= 0
            self.df['macd_signal'] = self.df['macdh_calc'].shift(1) != self.df['macdh_calc']
            self.df.loc[(self.df['macdh_calc'] == False) & (self.df['macd_signal'] == True) & (self.df['MACD_12_26_9'] < 0), f'{strat}'] = 'SELL'
            self.df.loc[(self.df['macdh_calc'] == True) & (self.df['macd_signal'] == True) & (self.df['MACD_12_26_9'] > 0), f'{strat}'] = 'BUY'

            signal = self.df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol', f'{strat}']]
            return signal

        elif strat == 'bop':
            self.df['BOP_calc'] = 0
            self.df['BOP_14'] = 0
            self.df['BOP_14'] = self.df['BOP'].rolling(14).mean()
            self.df.loc[(self.df['BOP_14'] < 0), 'BOP_calc'] = -1
            self.df.loc[(self.df['BOP_14'] > 0), 'BOP_calc'] = 1
            self.df.loc[(self.df['BOP_calc'] == 1) & (self.df['BOP_calc'].shift(1) == -1), f'{strat}'] = 'BUY'
            self.df.loc[(self.df['BOP_calc'] == -1) & (self.df['BOP_calc'].shift(1) == 1), f'{strat}'] = 'SELL'
            signal = self.df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol', f'{strat}']]
            return signal

        elif strat == 'ema':
            self.df.loc[(self.df['EMA_100'] <= self.df['Close']), 'ema'] = 'BUY'
            self.df.loc[(self.df['EMA_100'] >= self.df['Close']), 'ema'] = 'SELL'
            signal = self.df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol', f'{strat}']]
            return signal

        elif strat == 'bbands':
            self.df.loc[(self.df['BBU_5_2.5'] < self.df['High']), 'bbands'] = 'SELL'
            self.df.loc[(self.df['BBL_5_2.5'] > self.df['Low']), 'bbands'] = 'BUY'
            signal = self.df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol', f'{strat}']]
            return signal

        else:
            print(f'no {strat}.')
            pass


if __name__ == '__main__':
    dingdong = BackTester(strategy=StrategyOne,
                          db=db_obj,
                          interval=15,
                          start_date=None,
                          end_date=None,
                          signals=['bbands', 'ichimoku'],
                          sl=.05,
                          tp=.01)
