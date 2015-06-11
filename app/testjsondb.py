
from frauddb import *
import psycopg2
from psycopg2.extras import Json
import random
import json
import datetime


'''
 

 create table mytable (jsondata json)

'''

dbname = 'frauddb'
tablename = 'mytable'
#user = 'joyceduan'
user = 'gSchool'



print '\n',1, 'open database'
conn, cur = get_db(dbname = dbname)
#conn = psycopg2.connect(dbname=dbname, user='postgres', host='/tmp')
#cur = conn.cursor()
#conn.commit()

# #print 2
# #create_db(cur)

# print '\n',2, 'create table if not eixsting'
# create_tables(cur)
# conn.commit()

sql = "insert into mytable (jsondata) values (%s)" % [Json({'a': 100})]

print sql
cur.execute(sql)

