import pandas
import os
import pickle

"""
After running backtester.py you will have pickles with results from your backtest. You can view and export
these results running the read_results function. You can set the start time with the start_time variable. 
pkl_looper by default loops all the results from the directory and returns a csv table for each. 
"""

start_time = "2021-01-01 00:30:00"


def read_results(indicators_interval, start_date_time):
    with open(f'{indicators_interval}', 'rb') as f:
        result = pickle.load(f)
    sorting_dict = {
        "Indicators": [],
        "Outcome": [],
        "Trades": [],
        "TP": [],
        "TP_profit": [],
        "SL": [],
        "SL_profit": [],
        "Longs": [],
        "Longs_profit": [],
        "Shorts": [],
        "Shorts_profit": [],
        "Indicator_exit": [],
        "Indicator_exit_profit": [],
        "Timedelta_median": []
    }
    for key in result.keys():
        result_frame = result[key]
        # do things with the df
        result_frame = result_frame[(pandas.to_datetime(result_frame['Time']) >= pandas.to_datetime(start_date_time))]
        if result_frame.query('Type == "SHORT"').empty == False and result_frame.query('Type == "LONG"').empty == False:
            sorting_dict["Indicators"].append(key)
            sorting_dict["Outcome"].append(result_frame['outcome'].sum())
            sorting_dict["Trades"].append(len(result_frame))
            if result_frame.query('TP_SL == "TP"')['outcome'].sum() == 0.00:
                sorting_dict["TP"].append("0")
            else:
                sorting_dict["TP"].append(result_frame["TP_SL"].value_counts()["TP"])
            sorting_dict["TP_profit"].append(result_frame.query('TP_SL == "TP"')['outcome'].sum())
            if result_frame.query('TP_SL == "SL"')['outcome'].sum() == 0.00:
                sorting_dict["SL"].append("0")
            else:
                sorting_dict["SL"].append(result_frame["TP_SL"].value_counts()["SL"])
            sorting_dict["SL_profit"].append(result_frame.query('TP_SL == "SL"')['outcome'].sum())
            sorting_dict["Longs_profit"].append(result_frame.query('Type == "LONG"')['outcome'].sum())
            sorting_dict["Longs"].append(result_frame["Type"].value_counts()["LONG"])
            sorting_dict["Shorts"].append(result_frame["Type"].value_counts()["SHORT"])
            sorting_dict["Shorts_profit"].append(result_frame.query('Type == "SHORT"')['outcome'].sum())
            if result_frame.query('TP_SL == False')['outcome'].sum() == 0.00:
                sorting_dict["Indicator_exit"].append("0")
            else:
                sorting_dict["Indicator_exit"].append(result_frame["TP_SL"].value_counts()[False])
            sorting_dict["Indicator_exit_profit"].append(result_frame.query('TP_SL == False')['outcome'].sum())
            sorting_dict["Timedelta_median"].append(result_frame.sort_values("Timedelta")["Timedelta"].median())

    reporting_df = pandas.DataFrame.from_dict(sorting_dict)
    reporting_df = reporting_df.sort_values("Outcome")
    # print(reporting_df)
    reporting_df.to_csv(f'{indicators_interval}_{start_date_time[0:7]}.csv')
    with pandas.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified
        print(reporting_df.tail(3))


def pkl_looper():
    for pkl in os.listdir():
        if pkl[-4:] == '.pkl':
            print(pkl)
            read_results(pkl, start_time)


pkl_looper()
