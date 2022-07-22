import sqlite3
import pandas as pd


class DBHandler(object):
    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.conn = sqlite3.connect(f'{self.db}', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def query_main(self):
        """returns the values of the DB as a pd.df"""
        a = f'SELECT * FROM {self.table}'
        df = pd.read_sql_query(a, self.conn)
        return df

    def check_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(self.cursor.fetchall())

    def trunc_db(self, sure=False):
        if not sure:
            print(f'{self.table} is NOT dropped. Pass sure=True if you really want to drop the table.')
        else:
            try:
                self.conn.execute(f'DROP TABLE {self.table}')
            except Exception as e:
                print(f'{e}, table was not dropped because: ')

    def append_db(self, df):
        df.to_sql(self.table, self.conn, if_exists='append', index=False)

    def replace_last_entry(self, df):
        self.cursor.execute(f"""SELECT * FROM {self.table} WHERE Time = '{df['Time'][0]}'""")
        a = self.cursor.fetchall()
        if a:
            self.cursor.execute(f"""
            UPDATE {self.table}
            SET
            Open = '{df['Open'][0]}',
            High = '{df['High'][0]}',
            Low = '{df['Low'][0]}',
            Close = '{df['Close'][0]}',
            Volume = '{df['Volume'][0]}'
            WHERE
            Time = '{df['Time'][0]}'""")
            self.conn.commit()
        elif not a:
            self.append_db(df)


# SYMBOL = 'BTCUSDT'
# INTERVAL = '1m'
# db_obj = DBHandler(db=f'{SYMBOL}.db', table=f"""{SYMBOL}_Futures""")
# print(db_obj.query_main())

