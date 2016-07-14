"""

A simple script to visualise hospital locations and contact details
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
from bokeh.layouts import column


def QueryDB(sql, location='sqlite:////Users/saminiemi/Projects/myNHS/data/myNHS.db'):
    """

    :param sql:
    :param location:

    :return: dataframe

    """
    disk_engine = create_engine(location)
    df = pd.read_sql_query(sql, disk_engine)

    return df

def createMap(data):
    # unique names
    ops = list(data['DisplayName'].unique())

    # data
    msk = data['DisplayName'] == ops[0]
    source = ColumnDataSource(data=dict(lat=data['Latitude'][msk], lon=data['Longitude'][msk],
                                      disp=data['DisplayName'][msk],
                                      name=data['OrganisationName'][msk], postcode=data['Postcode'][msk],
                                      Address1=data['Address1'][msk], Address2=data['Address2'][msk],
                                      Address3=data['Address3'][msk],
                                      contact=data['OrganisationContactValue'][msk]))

    all = {}
    for o in ops:
        msk = data['DisplayName'] == o
        all[o] = dict(lat=data['Latitude'][msk], lon=data['Longitude'][msk],
                                      disp=data['DisplayName'][msk],
                                      name=data['OrganisationName'][msk], postcode=data['Postcode'][msk],
                                      Address1=data['Address1'][msk], Address2=data['Address2'][msk],
                                      Address3=data['Address3'][msk],
                                      contact=data['OrganisationContactValue'][msk])
    all = ColumnDataSource(all)

    # create figure
    bk.output_file("InformationMap.html", mode="cdn")
    fig = GMapPlot(plot_width=800, plot_height=700, logo=None,
                 x_range=Range1d(), y_range=Range1d(),
                 map_options=GMapOptions(lat=53.4808, lng=-1.2426, zoom=7),
                 api_key='AIzaSyBQH3HGn6tpIrGxekGGRAVh-hISYAPsM78')
    fig.map_options.map_type = "roadmap"
    fig.title.text = "Hospital Location and Contact Details"

    # hovering information
    hover = HoverTool(tooltips=[("Type:", "@disp"),
                                ("Name", "@name"),
                                ("Address", "@Address1 @Address2 @Address3"),
                                ("Postcode", "@postcode"),
                                ("Phone", "@contact")])

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
    bk.show(column(select, fig))

def run():
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
b.organisationContactMethodTypeID = 1'''
    data = QueryDB(sql)
    print(data.info())
    createMap(data)

if __name__ == "__main__":
    run()
