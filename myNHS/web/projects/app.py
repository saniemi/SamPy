"""
myNHS Dashboard Backend
=======================

A simple backend to provide data for the myNHS example Dashboard.


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
:date: 19-Jul-2016
"""
import pandas as pd
from flask import Flask
from flask import render_template
from SamPy.myNHS.analysis import hipReplacements as nhs


app = Flask(__name__)


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
    a.organisationID = b.organisationID and
    a.organisationTypeID = c.OrganisationTypeID and
    b.organisationContactMethodTypeID = 1 and
	a.Latitude != "" and a.Longitude != "" and
	a.OrganisationName != "" and a.Postcode != ""
	order by a.OrganisationName'''

    data = nhs.QueryDB(sql)

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
    a.organisationID = b.organisationID and
    b.metricID = c.metricID and
	b.treatmentID = d.treatmentID and
    b.metricID = 7 and
    a.Latitude != "" and a.Longitude != "" and a.OrganisationName != "" and
	c.isDeleted = 0'''

    data = nhs.QueryDB(sql)

    # change values to numeric
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
    data['Value'].fillna(value=0, inplace=True)

    data = data.to_json(orient='records')

    return data


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5555, debug=True)

