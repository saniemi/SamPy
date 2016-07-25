"""
myNHS Dashboard Backend
=======================

A simple backend to provide data for the myNHS example Dashboard.


Requirements
------------

:requires: Flask
:requires: pandas
:requires: sqlalchemy


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.2
:date: 25-Jul-2016
"""
import pandas as pd
from flask import Flask
from flask import render_template
from sqlalchemy import create_engine


app = Flask(__name__)


def QueryDB(sql, location='sqlite:////Users/saminiemi/Projects/myNHS/data/myNHS.db'):
    """

    :param sql:
    :param location:

    :return: dataframe

    """
    disk_engine = create_engine(location)
    df = pd.read_sql_query(sql, disk_engine)

    return df


@app.route("/")
def index():
    """

    :return:
    """
    return render_template("index.html")


@app.route("/organisationFinder.html")
def finder():
    """

    :return:
    """
    return render_template("organisationFinder.html")


@app.route("/operations.html")
def operations():
    """

    :return:
    """
    return render_template("operations.html")


@app.route("/waitTime.html")
def waiting():
    """

    :return:
    """
    return render_template("waitTime.html")


@app.route("/myNHS/finderData")
def finderData():
    sql = '''select
    a.OrganisationName, a.Address1, a.Address2, a.Address3, a.postcode, a.Latitude, a.Longitude,
    b.organisationContactValue,
    c.DisplayName
    from
    organisation as a,
    organisationContact as b,
    organisationType as c
    where
    b.organisationContactMethodTypeID = 1 and
    a.Latitude != "" and a.Longitude != "" and
	a.OrganisationName != "" and a.Postcode != "" and
    a.organisationID = b.organisationID and
    a.organisationTypeID = c.OrganisationTypeID
	order by a.OrganisationName'''

    data = QueryDB(sql)

    data = data.to_json(orient='records')

    return data


@app.route("/myNHS/operationsData")
def operationsData():
    sql = '''select
    a.OrganisationName, a.OrganisationTypeID, a.Latitude, a.Longitude, a.Address1, a.Address2, a.Address3, a.postcode,
    b.value, b.text, b.TreatmentID, b.isCurrentLastModified,
    c.DisplayName,
	 d.TreatmentName
    from
    organisation as a,
    indicator as b,
    metric as c,
	treatment as d
    where
    b.metricID = 7 and
    a.Latitude != "" and a.Longitude != "" and a.OrganisationName != "" and
	c.isDeleted = 0 and
    a.organisationID = b.organisationID and
    b.metricID = c.metricID and
	b.treatmentID = d.treatmentID
	order by a.OrganisationName
   '''
    data = QueryDB(sql)

    # change values to numeric
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
    data['Value'].fillna(value=0, inplace=True)

    # convert to JSON
    data = data.to_json(orient='records')

    return data


@app.route("/myNHS/waitTimeData")
def waitTimeData():
    sql = '''select
    a.OrganisationName, a.OrganisationTypeID, a.Latitude, a.Longitude, a.Address1, a.Address2, a.Address3, a.postcode,
    a.isPimsManaged,
    b.value, b.text, b.isCurrentLastModified,
    c.DisplayName,
	e.ServiceName
    from
    organisation as a,
    indicator as b,
    metric as c,
	indicatorservice as d,
	service as e
    where
    a.Latitude != "" and a.Longitude != "" and a.OrganisationName != "" and
	c.isDeleted = 0 and a.OrganisationStatusID = 1 and
    a.organisationID = b.organisationID and
	b.indicatorID = d.indicatorID and
	d.serviceID = e.serviceID and
    b.metricID = c.metricID and
    b.metricID = 64'''

    data = QueryDB(sql)

    # change values to numeric
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
    data['Value'].fillna(value=0, inplace=True)

    # change pims to "yes" and "no"
    data.replace(to_replace={'IsPimsManaged': {0: 'No', 1: 'Yes'}}, inplace=True)

    # convert to JSON
    data = data.to_json(orient='records')

    return data


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5555, debug=True)

