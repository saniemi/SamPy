"""

A simple script to visualise hospital locations and performance metrics
from NHS data.


Requirements
------------

:requires: pandas
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
from sqlalchemy import create_engine
import bokeh.plotting as bk
from bokeh.models import GMapPlot, Range1d, GMapOptions, ColumnDataSource, Circle
from bokeh.models import PanTool, BoxZoomTool, WheelZoomTool, HoverTool
from bokeh.models.widgets import Select
from bokeh.models import CustomJS
from bokeh.layouts import row


def QueryDB(sql, location='sqlite:////Users/saminiemi/Projects/myNHS/data/myNHS.db'):
    """

    :param sql:
    :param location:

    :return: dataframe

    """
    disk_engine = create_engine(location)
    df = pd.read_sql_query(sql, disk_engine)

    return df


def createMap(data, selectorColumn='MetricName'):
    # unique names
    ops = list(data[selectorColumn].unique())

    # data
    msk = data[selectorColumn] == ops[0]
    source = ColumnDataSource(data=dict(lat=data['Latitude'][msk], lon=data['Longitude'][msk],
                                        disp=data['DisplayName'][msk], metric=data['MetricName'][msk],
                                        name=data['OrganisationName'][msk],
                                        value=data['Value'][msk]))

    all = {}
    for o in ops:
        msk = data[selectorColumn] == o
        all[o] = dict(lat=data['Latitude'][msk], lon=data['Longitude'][msk],
                                        disp=data['DisplayName'][msk], metric=data['MetricName'][msk],
                                        name=data['OrganisationName'][msk],
                                        value=data['Value'][msk])
    all = ColumnDataSource(all)

    # create figure
    bk.output_file("MetricsMap.html", mode="cdn")
    fig = GMapPlot(plot_width=800, plot_height=700, logo=None,
                 x_range=Range1d(), y_range=Range1d(),
                 map_options=GMapOptions(lat=53.4808, lng=-1.2426, zoom=7),
                 api_key='AIzaSyBQH3HGn6tpIrGxekGGRAVh-hISYAPsM78')
    fig.map_options.map_type = "roadmap"
    fig.title.text = "Performance Metrics"

    # hovering information
    hover = HoverTool(tooltips=[("Name", "@name"),
                                ("Metrics", "@metric"),
                                ("Value", "@value")])

    # add tools
    fig.add_tools(PanTool(), BoxZoomTool(), WheelZoomTool(), hover)

    # add data
    circle = Circle(x="lon", y="lat", size=5, fill_color="blue",
                    fill_alpha=0.8, line_color=None)
    fig.add_glyph(source, circle)

    # create callback
    callback = CustomJS(args=dict(source=source), code="""
        var f = cb_obj.get('value');
        var d = all.get('data')[f];

        source.set('data', d);
        source.trigger('change');
        """)
    callback.args["source"] = source
    callback.args["all"] = all
    # Set up widgets
    select = Select(title="Select", value=ops[0], options=ops, callback=callback)

    # show the map
    bk.show(row(select, fig))

def run():
    sql = '''select
    a.OrganisationName, a.Latitude, a.Longitude,
    b.MetricID, b.Value, b.Text,
    c.MetricName, c.DisplayName
    from
    organisation as a,
    indicator as b,
    metric as c
    where
    a.organisationID = b.organisationID and
    b.metricID = c.metricID and
    b.metricID in (7, 64) and
    b.isCurrent = 1'''
    #b.metricID in (7, 64, 67, 97, 190, 439, 2304, 5040) and
    data = QueryDB(sql)
    print(data.info())
    print(data.head(5))
    createMap(data)

if __name__ == "__main__":
    run()

