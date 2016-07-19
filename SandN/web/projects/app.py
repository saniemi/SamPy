"""
Smith & Nephew Dashboard Backend
================================


A simple backend to provide data for the Smith & Nephew Dashboard Demo example Dashboard.


Requirements
------------

:requires: Flask
:requires: pandas
:requires: numpy


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 18-Jul-2016
"""
from flask import Flask
from flask import render_template
from SamPy.myNHS.analysis import hipReplacements as nhs
import pandas as pd
import numpy as np


np.random.seed(12345)

app = Flask(__name__)


@app.route("/")
def index():
    """

    :return:
    """
    return render_template("index.html")


@app.route("/hipReplacement.html")
def hips():
    """

    :return:
    """
    return render_template("hipReplacement.html")


@app.route("/myNHS/hipReplacements")
def hipReplacements():
    """

    :return:
    """
    sql = '''select
    a.OrganisationName, a.Address1, a.Address2, a.Address3, a.postcode,
    a.Latitude, a.Longitude, a.OrganisationTypeID, a.isPimsManaged,
    b.value, isCurrentLastModified,
    c.metricName
    from
    organisation as a,
    indicator as b,
    metric as c
    where
    a.organisationID = b.organisationID and
    b.metricID = c.metricID and
    b.metricID = 9225'''

    data = nhs.QueryDB(sql)

    # chagen values to numeric
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
    data['Value'].fillna(value=0, inplace=True)

    # change pims to "yes" and "no"
    data.replace(to_replace={'IsPimsManaged': {0: 'No', 1: 'Yes'}}, inplace=True)

    # add some fake data
    rows = len(data.index)
    data['Views'] = np.random.randint(1000, 20000, size=rows)
    data['Probability'] = np.random.randint(1, 4, size=rows)
    data.replace(to_replace={'Probability': {1: 'Low', 2: 'Moderate', 3: 'High'}}, inplace=True)

    data = data.to_json(orient='records')

    return data


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5555, debug=True)

