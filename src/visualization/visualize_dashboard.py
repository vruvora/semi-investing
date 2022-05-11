from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_table


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)




app.layout = html.Div([
    html.H3('Keep Semi-Conductors Deflationary'),
    dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
        dcc.Tab(label='Tab One', value='tab-1-example-graph'),
        dcc.Tab(label='Tab Two', value='tab-2-example-graph'),
        dcc.Tab(label='Talent & Energy Hubs', value='talent-map'),

    ]),
    html.Div(id='tabs-content-example-graph')
])

@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-example-graph', 'value'))
def render_content(tab):
    if tab == 'tab-1-example-graph':
        return html.Div([
            html.H3('Tab content 1'),
            dcc.Graph(
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [3, 1, 2],
                        'type': 'bar'
                    }]
                }
            )
        ])
    elif tab == 'tab-2-example-graph':
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                id='graph-2-tabs-dcc',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [5, 10, 6],
                        'type': 'bar'
                    }]
                }
            )
        ])
    elif tab == 'talent-map':
        df = pd.read_csv('data/processed/electricity_prices.csv').sort_values(by="Number of Indeed Jobs", ascending=False)
        return html.Div([
            html.Div([
              dcc.Graph(id='map', figure=build_map())
            ]),
            html.Div([
              dcc.Graph(id='energy', figure=build_energy_graph())
            ]),
            dash_table.DataTable(
                id='net_cash_table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
            )
        ])

def build_map():
    indeed_lat_long = pd.read_csv('data/processed/indeed_lat_long.csv')
    limits = [(1,3),(3,10),(10,50),(50,300)]
    colors = ["royalblue","crimson","lightseagreen","orange"]
    cities = []
    scale = 5000
    limits = [(1,3),(3,10),(10,50),(50,300)]
    colors = ["royalblue","crimson","lightseagreen","orange"]
    cities = []
    scale = 5000

    fig = go.Figure()

    for i in range(len(limits)):
        lo, hi = limits[i]
        df_sub = indeed_lat_long[(indeed_lat_long['count'] >= lo) & (indeed_lat_long['count'] < hi)]
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
            title_text = 'Fabrication Engineers and Computer Architecture Jobs in the US (10K+ Listings)',
            title_x = 0.5,
            showlegend = True,
            geo = dict(
                scope = 'usa',
                landcolor = 'rgb(217, 217, 217)',
            )
        )

    return fig

def build_energy_graph():
    use_energy = pd.read_csv('data/processed/electricity_prices.csv')
    fig = px.scatter(use_energy, x="Number of Indeed Jobs", y="Average retail price (cents/kWh)", text='Name', trendline="ols", log_x=True)
    fig.update_layout(
            title_text = 'Relationship between Fabrication Jobs and Energy Costs at the Location of the Job',
            title_x = 0.5,
            showlegend = True,
            geo = dict(
                scope = 'usa',
                landcolor = 'rgb(217, 217, 217)',
            )
        )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)