'''
todo:
1. dump database
2. write out instruction on setup database

------------
Set up postgres database:
on command line
1.  start postgres database
2. psql
        CREATE DATABASE frauddbv2;
        \q

-------------
This script:
create postgres database
table: events
    object_id integer PRIMARY KEY,
    score text,
    manual_flag boolean,
    ts_received timestamp,
    data jsonb);

'''

import psycopg2
from psycopg2.extras import Json
import random
import json
import datetime

dbname = 'frauddbv2'
tablename = 'events'
user = 'gSchool'
#user = 'joyceduan'
#user = 'postgres'

def get_db(dbname = dbname, user = user):
    '''
    get connection to frauddb database
     - INPUT: string, string
     - OUTPUT: connection, cursor
    '''
    conn_fraud = psycopg2.connect(dbname=dbname, user=user, host='/tmp')
    cur_fraud = conn_fraud.cursor()
    conn_fraud.commit()

    #conn.close()
    #conn = psycopg2.connect(database="testdb", user="postgres", password="pass123", host="127.0.0.1", port="5432")
    print "-------------\n Opened database %s successfully" %(dbname)
    return conn_fraud, cur_fraud


#def store_1_row(cur, score):
def store_1_row(cur, data, score, timestamp, conn ):
    '''
    insert one row to table events  
    - INPUT:
            cur    cursor to coonnect to the databse 
            score  float
           data  datafrmae tbd??
           timestamp  the data is received
    - OUTOUT: None
    '''

    obj_id = data['object_id']
    
    # sql = '''
    #     INSERT INTO %s  (object_id, score, ts_received, data)  VALUES (%d, %.3f, '%s', "%s") 
    #        ''' %(tablename, obj_id, score, timestamp, data)

    # #the following does not hangel NULL flag correctly
    # #flag = None
    # #sql = '''
    # #insert into %s values (%d, %.3f, %s, '%s', %s ) 
    # #''' % (tablename, obj_id, score, flag, timestamp, Json(data))
    # print 'sql:'
    # print sql

    # cur.execute(sql)

    t = str(data).decode('utf8')
    t = t.replace('%', '%%')
    t = t.replace("'", '"')
    try:
        sql = '''
        INSERT INTO %s  (object_id, score, ts_received, data)  VALUES (%s, %.3f, '%s', '%s') 
        ''' % (tablename, obj_id, score, timestamp, t)

        # sql = '''
        # INSERT INTO %s  (object_id, score, ts_received)  VALUES (%s, %.3f, '%s');
        # ''' % (tablename, obj_id, score, timestamp) 

        print sql[:150]
        cur.execute(sql)
        conn.commit()
    except: 
        pass
    # cur.execute("insert into %s  (object_id, score, ts_received, data)  values \
    #     (%d, %.3f, %s, %s)", (tablename, obj_id, score, timestamp, t))

def get_most_recent_k(cur, k=20):
    '''
    get a subset (k most recent records sorted by score)
    - INPUT: k: 
    - OUTPUT:  list of list 
                [obj_id, score, flag, timestamp, json_data]

        results = get_most_recent_k(cur)
        for result in results:
            obj_id = result[0]
            score = result[1]
            flag = result[2]
            timestamp = result[3]
            json_data = result[4]
    '''
    sql = '''
    select * from %s order by ts_received desc limit %d 
    ''' % (tablename, k)
    cur.execute(sql)
    results = cur.fetchall()
    #for res in results:
    #    print res
    return results

def update_row(cur, conn, obj_id, flag):
    '''
    update the manual_flag for a record
    '''
    sql_update = '''
    UPDATE %s SET manual_flag = %s WHERE object_id = %d;
    ''' % (tablename, flag, obj_id)
    print sql_update
    cur.execute(sql_update)
    conn.commit()

def create_tables(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS events  (
            object_id integer, -- PRIMARY KEY,
            score text,
            manual_flag boolean,
            ts_received timestamp,
            data text); 
        ''')
    print 'table %s exists/created' % ('events')


def test_get_one():
    '''
    get one event as json object
     - OUTPUT: json
    '''
    with open('data/example.json') as data_file:    
        data = json.load(data_file)
    score = random.random()
    timestamp = datetime.datetime.now()
    return data, score, timestamp


def main():
    pass 


if __name__ == '__main__':
   # main()
    print '\n',1, 'open database'
    conn, cur = get_db(dbname = dbname)
    #conn = psycopg2.connect(dbname=dbname, user='postgres', host='/tmp')
    #cur = conn.cursor()
    #conn.commit()

    #print 2
    #create_db(cur)

    print '\n',2, 'create table if not eixsting'
    create_tables(cur)
    conn.commit()

    data, score, timestamp = test_get_one()
    #print score, timestamp
    #print data
    print '\n',3, 'insert one data row'
    store_1_row(cur, data, score, timestamp, conn)
    conn.commit()

    print '\n',4, 'get most recent data from the database'
    results = get_most_recent_k(cur)
    for result in results:
        obj_id = result[0]
        score = result[1]
        flag = result[2]
        timestamp = result[3]
        json_data = result[4]
        print 'obj_id:', obj_id
        print 'score:', score
        print 'manual flag:', flag
        print 'timestamp:', timestamp
        print 'data', json_data
        print "\n"

    print '\n', 5, 'update the manual_flag'
    obj_id = 5558108
    flag = True
    update_row (cur, conn, obj_id, flag)
    #fill_tables(coll, cur)
    #create_indices(cur)????

    conn.commit()
    conn.close()


'''
example data

{"org_name": "DREAM Project Foundation", "name_length": 51, "event_end": 1363928400, "venue_latitude": 42.9630578, "event_published": 1361978554.0, "user_type": 1, "channels": 11, "currency": "USD", "org_desc": "", "event_created": 1361291193, "event_start": 1363914000, "has_logo": 1, "email_domain": "dreamprojectfoundation.org", "user_created": 1361290985, "payee_name": "", "payout_type": "ACH", "venue_name": "Grand Rapids Brewing Co", "sale_duration2": 30, "venue_address": "1 Ionia Avenue Southwest", "approx_payout_date": 1364360400, "org_twitter": 13.0, "gts": 537.4, "listed": "y", "ticket_types": [{"event_id": 5558108, "cost": 50.0, "availability": 1, "quantity_total": 125, "quantity_sold": 10}], "org_facebook": 13.0, "num_order": 7, "user_age": 0, "body_length": 1474, "description": "<p><span style=\"font-size: medium; font-family: 'book antiqua', palatino;\">Come enjoy a night of music and beer tasting at the new Grand Rapids Brewery while we make an effort to create awareness and raise funds for Dream Project Foundation. The night will include music, Grand Rapids Brewery's finest beer to sample, heavy hors d'oeuvre's and silent auction of artwork directly from the young artists of Dream House.</span></p>\r\n<p>&nbsp;</p>\r\n<p>Who We Are:</p>\r\n<p>DREAM Project Foundation is a small American 501c3 registered non-profit organization, working to break the cycle of human trafficking through community development. As a small, grass roots organization, we focus primarily on prevention and protection which begins with shelter and continues with education, so those vulnerable are aware of the dangers and able to protect themselves.</p>\r\n<p>DREAM Project Foundation was officially founded in 2011 to support the DREAM House children's home based in Thailand on the border of Myanar (Burma). While helping children stay safe from the trafficing is the heart of our mission, we know that in order to end trafficking it must be a collaborative effort for all people and communities.&nbsp;</p>\r\n<p>We at DREAM Project Foundation are determined to fight against this atrocity, focusing on the factors that cause people to be vulnerable targets to traffickers, with most of our work based in SE Asia as it is a major international hub of human trafficking.</p>", "object_id": 5558108, "venue_longitude": -85.6706147, "venue_country": "US", "previous_payouts": [{"name": "", "created": "2013-04-19 03:25:42", "country": "US", "state": "", "amount": 500.0, "address": "", "zip_code": "", "event": 5558108, "uid": 52778636}], "sale_duration": 22.0, "num_payouts": 0, "name": "DREAM Project Foundation - Taste of a Better Future", "country": "US", "delivery_method": 0.0, "has_analytics": 0, "fb_published": 0, "venue_state": "MI", "has_header": null, "show_map": 1}
'''
