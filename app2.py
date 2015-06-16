from flask import Flask, request, render_template
import json
import requests
import socket
import time
import cPickle as pickle
from datetime import datetime

import plotly.plotly as py
from plotly.graph_objs import *
import numpy as np
#Username: jim.knudstrup
#API Key: mn4lcoy1du
# python -c "import plotly; plotly.tools.set_credentials_file(username='jim.knudstrup', api_key='mn4lcoy1du')"
"""
<iframe width="640" height="480" frameborder="0" seamless="seamless" scrolling="no" 
src="https://plot.ly/~jim.knudstrup/12.embed?width=640&height=480" ></iframe>
"""

#import Suhan's predict
#import Joyce's DB API

app = Flask(__name__)
PORT = 5353
REGISTER_URL = "http://10.3.33.9:5000/register"
DATA = []
TIMESTAMP = []

def gen_colors(probabilities):
    """
    Input: list of probabilities (floats)
    Output: list of colors (strings of hex codes)
    Takes in probabilities and color codes them for graphing.
    Red: High Risk
    Yellow: Medium Risk
    Green: Low Risk
    """
    colors = []
    for prob in probabilities:
        if prob >= .8:
            colors.append('#c75959')
        elif prob >= .5:
            colors.append('#c0ce53')
        else:
            colors.append('#74df49')
    return colors

def build_trace(rn, rise, color_list):
    """Makes a bar plot trace and returns it."""
    data = Data([
        Bar(
            x=rn, 
            y=rise, 
            name="Recent Activity", 
            marker=Marker(color=color_list)
            )
        ])
    return data

def build_layout():
    """Builds and returns a plotly layout."""
    title = "Fraud Detector: Recent Activity"
    layout = Layout(
        title=title,
        showlegend=False,
        yaxis=YAxis(
            title="Probability",
            zeroline=False))
    return layout

@app.route('/')
@app.route('/index')
def index():
    #Testing to see to it that I can output something to the dashboard
    name = "default"
    if DATA and TIMESTAMP:
        data = json.loads(DATA[-1])
        name = data['email_domain']#"email_domain": "watercoolerhub.com",

    #Get 20 predictions
    #Get 20 timestamps
    #Feed into plot
    #get iframe?
    labels = range(20) #timestamps
    probs = np.random.random(size=20) #predictions
    colors = gen_colors(probs)

    data = build_trace(labels, probs, colors)
    layout = build_layout()
    fig = Figure(data=data, layout=layout)


    plot_url = py.plot(fig, filename='Recent-Transactions', auto_open=False)

    return render_template('index.html', data=name)


@app.route('/score', methods=['POST'])
def score():
    #Store/assign POST data 
    DATA.append(json.dumps(request.json, sort_keys=True, indent=4, separators=(',', ': ')))
    #Store/assign timestamp data
    TIMESTAMP.append(time.time())
    #Generate/assign prediction with predict(data, model, ...)
    #Store data, prediction, timestamp etc... in DB
    return ""


@app.route('/check')
def check():
    line1 = "Number of data points: {0}".format(len(DATA))
    if DATA and TIMESTAMP:
        dt = datetime.fromtimestamp(TIMESTAMP[-1])
        data_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        line2 = "Latest datapoint received at: {0}".format(data_time)
        line3 = DATA[-1]
        output = "{0}\n\n{1}\n\n{2}".format(line1, line2, line3)
    else:
        output = line1
    return output, 200, {'Content-Type': 'text/css; charset=utf-8'}


def register_for_ping(ip, port):
    registration_data = {'ip': ip, 'port': port}
    requests.post(REGISTER_URL, data=registration_data)


if __name__ == '__main__':
    # Register for pinging service
    ip_address = socket.gethostbyname(socket.gethostname())
    print "attempting to register %s:%d" % (ip_address, PORT)
    register_for_ping(ip_address, str(PORT))



    # Start Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)
