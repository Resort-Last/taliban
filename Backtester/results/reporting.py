import pandas
import pandas as pd
import os
import pickle


def read_results(indicators_interval, start_date_time):
    with open(f'{indicators_interval}', 'rb') as f:
        result = pickle.load(f)
    sorting_dict = {}
    for key in result.keys():
        result_frame = result[key]
        try:
            # do things with the df
            sorting_dict[key] = [result_frame['outcome'].sum(), "other results"]
        except:
            pass
    sorting_dict = dict(sorted(sorting_dict.items(), key=lambda item: item[1], reverse=True))
    print(sorting_dict)


for pkl in os.listdir():
    if pkl != 'reporting.py':
        print(pkl)
        read_results(pkl, "2021-08-12 00:30:00")



"""
pkl ek elnevezese, legyen benne a TA neve
kiszedni 0 valuekat
plusz adatok gitrol
function legyen aminek parameter hogy melyik pkl 
    a fuction valassza ki a pikeleket amik megfelelnek a parametereknek
    kiirja a top dolgokat
"""