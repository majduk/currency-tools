#!/usr/bin/python3

import pandas as pd
from matplotlib import pyplot
from sqlalchemy import create_engine
import pymysql

with open('db_pass.txt') as keyfile:
    db_pass = keyfile.read()

sqlEngine = create_engine('mysql+pymysql://dbuser:{}@127.0.0.1'.format(db_pass), pool_recycle=3600)
dbConnection = sqlEngine.connect()
series = pd.read_sql(sql = "select * from rates.usd", con = dbConnection, index_col='ts');

series.plot()
pyplot.show()
# #pyplot.savefig('/tmp/dupa.png')
