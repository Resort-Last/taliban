# taliban
not really a terrorist script, just a (t)ecnical (a)nalysis library for losing money (i just thought its a funnny name)

USAGE: 

Fill your API, symbol, interval etc. in the `config.py `

Set up your strategy in the `apply_strat.py ` 

    The strategy function has to return 2 values: entry and exit. 
    Valid values are BUY, SELL and pandas NoneType (pd.isna)

HOW TO RUN IT: 

1. Make sure to start the `stream_to_db.py` first. (in a separate cmd or ps.)

This function updates the db every second. 

2. run `main.py`

3. profit? 
