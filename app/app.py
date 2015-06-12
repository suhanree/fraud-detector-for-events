# Our main python program to run the web app.

from flask import Flask, request, render_template
import json
import requests
import socket
import time
import os
import sys
import cPickle as pickle
# import plotly.plotly as py

from model import buildmodel, predict
from frauddbv2 import *

app = Flask(__name__)
PORT = 5353
REGISTER_URL = "http://10.3.33.9:5000/register"
DATA = []
TIMESTAMP = []
SCORES = []

# Database-related variables.
dbname = 'frauddbv2'
tablename = 'events'
user = 'gSchool'
conn_fraud = None
cur_fraud = None

# Filename for the pickle object.
filename_pickle = 'data/model.pkl'

# Our model.
our_model = None

# Features we use from the original dataset.
# They are divided into two groups: category and non-category.
label_name = 'acct_type'
category_features = ['channels', 'country', 'currency', 'delivery_method',
                    'fb_published', 'has_analytics', 'has_header',
                    'has_logo', 'listed', 'payout_type', 'show_map',
                    'user_type', 'venue_country']
non_category_features = ['approx_payout_date', 'body_length', 'num_payouts',
                        'sale_duration', 'sale_duration2',
                        'user_age', 'venue_latitude', 'venue_longitude']

@app.route('/')
def index():
    #Testing to see to it that I can output something to the dashboard
    name = "default"
    if DATA and TIMESTAMP:
        data = json.loads(DATA[-1])
        name = data['email_domain']#"email_domain": "watercoolerhub.com",

    return render_template('index.html', data=name)



@ app.route('/score', methods=['POST'])
def score():
    #DATA.append(json.dumps(request.json))
    #TIMESTAMP.append(time.time())

    data_new = json.dumps(request.json)
    timestamp_new = datetime.datetime.now()

    # Predict with our model.
    data_json = json.loads(data_new)
    score = predict(data_json, our_model, final_columns,
                         category_features, averages)
    #SCORES.append(score)
    # save the data and prediction in our db.
    store_1_row(cur_fraud, data_json, score, timestamp_new)

    return ""


@app.route('/check')
def check():
    if DATA and TIMESTAMP:
        return "%d\n\n%s" % (TIMESTAMP[-1], DATA[-1]), 200,\
            {'Content-Type': 'text/css; charset=utf-8'}
    return "No data received"

def register_for_ping(ip, port):
    registration_data = {'ip': ip, 'port': port}
    requests.post(REGISTER_URL, data=registration_data)


if __name__ == '__main__':
    # Usage for rebuilding the model.
    print """If you want to rebuild the model, use "python app.py rebuild" """

    # If the pickle object doesn't exist or the rebuild option
    # is given by the command line.
    if (not os.path.exists(filename_pickle)) or \
        (len(sys.argv) > 1 and sys.argv[1] == 'rebuild'):
        (built_model, final_columns, averages) = \
            buildmodel(label_name, category_features,
                    non_category_features, model=our_model, save=True)
        print "Built the model, and saved as pickle in the file,", filename_pickle
    else:
        print "Reading pickled file for our model."
        with open(filename_pickle, 'r') as f:
            (built_model, final_columns, averages) = pickle.load(f)
    our_model = built_model

    # Get the database.
    dbname = 'frauddb'
    tablename = 'events'
    user = 'gSchool'
    conn_fraud, cur_fraud = get_db(dbname, user)

    # Register for pinging service
    ip_address = socket.gethostbyname(socket.gethostname())
    print "attempting to register %s:%d" % (ip_address, PORT)
    register_for_ping(ip_address, str(PORT))

    # Start Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)
