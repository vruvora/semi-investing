import plotly.graph_objects as go

import pandas as pd

df = pd.read_csv('data/processed/indeed_lat_long.csv')
df.head()

limits = [(1,3),(3,10),(10,50),(50,300)]
colors = ["royalblue","crimson","lightseagreen","orange"]
cities = []
scale = 5000

fig = go.Figure()

for i in range(len(limits)):
    lo, hi = limits[i]
    df_sub = df[(df['count'] >= lo) & (df['count'] < hi)]
    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon = df_sub['long'],
        lat = df_sub['lat'],
        text = df_sub['count'],
        marker = dict(
            size = df_sub['count']*10,
            color = colors[i],
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area'
        ),
        name = '{0} - {1}'.format(lo,hi)))

fig.update_layout(
        title_text = 'Fabrication Engineers and Computer Architecture Jobs in the US ',
        showlegend = True,
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )

fig.show()