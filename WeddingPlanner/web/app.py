"""
Wedding Planner Dashboard
=========================

A simple backend to provide data for the Wedding Planner Dashboard


Requirements
------------

:requires: Flask
:requires: pandas


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 01-Aug-2016
"""
import pandas as pd
from flask import Flask
from flask import render_template
from flask_compress import Compress
from flask_cache import Cache
from sqlalchemy import create_engine


app = Flask(__name__)
#Compress(app)
#cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def getTableFromStore(table, storename='/Users/saminiemi/Projects/WeddingPlanner/store.h5', verbose=False):
    df = pd.read_hdf(storename, table)

    if verbose:
        print(df.info())
        print(df.describe())

    return df


@app.route("/")
def index():
    """

    :return:
    """
    return render_template("index.html")


@app.route("/sessions.html")
def operations():
    """

    :return:
    """
    return render_template("sessions.html")


@app.route("/WeddingPlanner/sessions")
def waitTimeData():
    # get data from store
    data = getTableFromStore('sessions')

    # convert to JSON
    data = data.to_json(orient='records')

    return data


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5555, debug=True)

