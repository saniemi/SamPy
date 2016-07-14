"""

A simple script to visualise hospital metrics.

Requirements
------------

:requires: pandas
:requires: numpy
:requires: sqlalchemy
:requires: bokeh


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 14-Jul-2016
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import bokeh.plotting as bk
from bokeh.models import GMapPlot, Range1d, GMapOptions, ColumnDataSource, Circle
from bokeh.models import PanTool, BoxZoomTool, WheelZoomTool, HoverTool



def QueryDB(sql, location='sqlite:////Users/saminiemi/Projects/myNHS/data/myNHS.db'):
    """

    :param sql:
    :param location:

    :return: dataframe

    """
    disk_engine = create_engine(location)
    df = pd.read_sql_query(sql, disk_engine)

    return df


def scale(data, min=5, max=40):
    tmp = []
    for value in data:
        try:
            tmp.append(int(value))
        except:
            t = value.split(' ')
            tmp.append(int(t[-1]))
    data = np.asarray(tmp)

    new = (((data - data.min()) * (max - min)) / (data.max() - data.min())) + min

    return new


def createMap(data):
    # data
    scaled = scale(data['Value'].values)
    source = ColumnDataSource(data=dict(lat=data['Latitude'], lon=data['Longitude'],
                                        name=data['OrganisationName'], metric=data['MetricName'],
                                        value=data['Value'],
                                        scaled=scaled))


    # create figure
    bk.output_file("HipReplacementMap.html", mode="cdn")
    fig = GMapPlot(plot_width=800, plot_height=800, logo=None,
                 x_range=Range1d(), y_range=Range1d(),
                 map_options=GMapOptions(lat=53.4808, lng=-1.2426, zoom=7),
                 api_key='AIzaSyBQH3HGn6tpIrGxekGGRAVh-hISYAPsM78')
    fig.map_options.map_type = "roadmap"
    fig.title.text = "Hospitals - Number of Primary Hip Replacements in 12 Months"

    # hovering information
    hover = HoverTool(tooltips=[("Name", "@name"),
                                ("Metric", "@metric"),
                                ("Value", "@value")])

    # add tools
    fig.add_tools(PanTool(), BoxZoomTool(), WheelZoomTool(), hover)

    # add data
    circle = Circle(x="lon", y="lat", size='scaled',
                    fill_color="blue", fill_alpha=0.8, line_color=None)
    fig.add_glyph(source, circle)

    # show the map
    bk.show(fig)


def run():
    sql = '''select
    a.OrganisationName, a.Latitude, a.Longitude,
    b.value,
    c.metricName
    from
    organisation as a,
    indicator as b,
    metric as c
    where
    a.organisationID = b.organisationID and
    b.metricID = c.metricID and
    b.metricID = 9225 and
    b.isCurrent = 1'''
    data = QueryDB(sql)
    print(data.info())
    createMap(data)


if __name__ == "__main__":
    run()
