import pandas as pd
from vincent import (Visualization, Scale, DataRef, Data, PropertySet,
                     Axis, ValueRef, MarkRef, MarkProperties, Mark)

df = pd.DataFrame({'Data 1': [15, 29, 63, 28, 45, 73, 15, 62],
                   'Data 2': [42, 27, 52, 18, 61, 19, 62, 33]})

#Top level Visualization
vis = Visualization(width=500, height=300)
vis.padding = {'top': 10, 'left': 50, 'bottom': 50, 'right': 100}

#Data. We're going to key Data 2 on Data 1
vis.data.append(Data.from_pandas(df, columns=['Data 2'], key_on='Data 1', name='table'))

#Scales
vis.scales.append(Scale(name='x', type='ordinal', range='width',
                        domain=DataRef(data='table', field="data.idx")))
vis.scales.append(Scale(name='y', range='height', nice=True,
                        domain=DataRef(data='table', field="data.val")))

#Axes
vis.axes.extend([Axis(type='x', scale='x'), Axis(type='y', scale='y')])

#Marks
enter_props = PropertySet(x=ValueRef(scale='x', field="data.idx"),
                                     y=ValueRef(scale='y', field="data.val"),
                                     width=ValueRef(scale='x', band=True, offset=-1),
                                     y2=ValueRef(scale='y', value=0))
update_props = PropertySet(fill=ValueRef(value='steelblue'))
mark = Mark(type='rect', from_=MarkRef(data='table'),
            properties=MarkProperties(enter=enter_props,
            update=update_props))

vis.marks.append(mark)
vis.axis_titles(x='Data 1', y='Data 2')
vis.to_json('vega.json')