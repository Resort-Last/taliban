import pandas
import os
import pickle
from datetime import datetime

def read_results(indicators_interval, start_date_time):
    with open(f'{indicators_interval}', 'rb') as f:
        result = pickle.load(f)
    sorting_dict = {
        "Indicators" : [],
        "Outcome" : [],
        "Trades" : [],
        "Longs" : [],
        "Longs_profit" : [],
        "Shorts" : [],
        "Shorts_profit" : [],
        "Timedelta_median" : []
    }
    for key in result.keys():
        result_frame = result[key]
        # do things with the df
        result_frame = result_frame[(pandas.to_datetime(result_frame['Time']) >= pandas.to_datetime(start_date_time))]
        if result_frame.query('Type == "SHORT"').empty == False and result_frame.query('Type == "LONG"').empty == False:
            sorting_dict["Indicators"].append(key)
            sorting_dict["Outcome"].append(result_frame['outcome'].sum())
            sorting_dict["Trades"].append(len(result_frame))
            sorting_dict["Timedelta_median"].append(result_frame.sort_values("Timedelta")["Timedelta"].median())
            sorting_dict["Longs_profit"].append(result_frame.query('Type == "LONG"')['outcome'].sum())
            sorting_dict["Longs"].append(result_frame["Type"].value_counts()["LONG"])
            sorting_dict["Shorts"].append(result_frame["Type"].value_counts()["SHORT"])
            sorting_dict["Shorts_profit"].append(result_frame.query('Type == "SHORT"')['outcome'].sum())



            #reporting_df = pandas.DataFrame.from_dict(sorting_dict)
    reporting_df = pandas.DataFrame.from_dict(sorting_dict)
    reporting_df = reporting_df.sort_values("Outcome")
    # print(reporting_df)
    reporting_df.to_csv(f'{indicators_interval}.csv')
    with pandas.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(reporting_df.tail(3))


for pkl in os.listdir():
    if pkl[-4:] == '.pkl':
        print(pkl)
        read_results(pkl, "2022-01-01 00:30:00")



"""
pkl ek elnevezese, legyen benne a TA neve
kiszedni 0 valuekat
plusz adatok gitrol
function legyen aminek parameter hogy melyik pkl 
    a fuction valassza ki a pikeleket amik megfelelnek a parametereknek
    kiirja a top dolgokat
"""