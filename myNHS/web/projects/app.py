"""
myNHS Dashboard Backend
=======================

A simple backend to provide data for the myNHS example Dashboard.


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
	order by a.OrganisationName
	limit 1000'''

    data = nhs.QueryDB(sql)
    data = data.to_json(orient='records')

    return data

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5555, debug=True)

