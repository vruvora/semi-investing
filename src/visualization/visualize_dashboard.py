from re import S
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash
import dash_table
import random
import networkx as nx


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)




app.layout = html.Div([
    html.H3('Keep Semi-Conductors Deflationary'),
    dcc.Tabs(id="tabs-example-graph", value='asym-science', children=[
        dcc.Tab(label='Finding Asymetric Deep Tech Bets', value='asym-science'),
        dcc.Tab(label='Supply Chain Analytics', value='supply-chain'),
        dcc.Tab(label='Talent & Energy Hubs', value='talent-map'),

    ]),
    html.Div(id='tabs-content-example-graph')
])

@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-example-graph', 'value'))
def render_content(tab):

    if tab == 'asym-science':
        centrality_df = pd.read_csv("data/processed/author_centrality.csv")
        hetrogenous_df = centrality_df[centrality_df['Topic-Words'] == 'systems scheduling heterogeneous tasks distributed multiprocessor reducing decomposition cloud online']
        return html.Div([
            html.H3('What are scientiests working on?'),
            html.Div([
                dcc.Graph(id='topic_ts', figure=build_topic_evolution())
            ]),
            html.Div([
                dcc.Graph(id='topic_ts', figure=build_coauthorship_network())
            ]),
            dcc.Dropdown(
                id='topics-dropdown',
                options=[{'label': i, 'value': i} for i in centrality_df['Topic-Words'].unique()],
                value='systems scheduling heterogeneous tasks distributed multiprocessor reducing decomposition cloud online'
            ),
            dash_table.DataTable(
                id='centrality_authors',
                columns=[{"name": i, "id": i} for i in hetrogenous_df.columns],
                data=hetrogenous_df.to_dict('records')),
        ])
    elif tab == 'supply-chain':
        supplier_choke = pd.read_csv('data/processed/Supplier_Indegree_Score.csv')
        supplier_choke = supplier_choke[supplier_choke['Chokepoint Score'] > 0]
        supplier_choke['Chokepoint Score'] =  supplier_choke['Chokepoint Score'] / supplier_choke['Chokepoint Score'].sum()
        return html.Div([
            html.H3('Semi-Conductor Supply Chain Networks'),
            dcc.RadioItems(['Supplier', 'Customer'], 'Supplier', inline=True, id='partner_type'),
            html.Div([dcc.Graph(id='supply_graph')]),
            dcc.RadioItems(['Degree Centrality', 'Betweeness'], 'Degree Centrality', inline=True, id='choke_type'),
            dash_table.DataTable(id='choke_df', columns=[{"name": i, "id": i} for i in supplier_choke.columns], data=supplier_choke.to_dict('records')),
        ])
    elif tab == 'talent-map':
        df = pd.read_csv('data/processed/electricity_prices.csv').sort_values(by="Number of Indeed Jobs", ascending=False)
        return html.Div([
            html.H3("Where can we build Semi Infrastructure?"),
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


def build_coauthorship_network():
    edge_x = []
    edge_y = []
    filtered_authors = pd.read_csv('data/processed/filtered_authors.csv')
    topic_per_author = pd.read_csv('data/processed/topic_per_author.csv').set_index('author1')

    G = nx.from_pandas_edgelist(filtered_authors, source='author1', target='author2')
    node_colors = pd.read_csv('data/processed/node_colors.csv').set_index('author1')
    color_map_plotly = []
    colors_plotly = []
    for _ in range(14):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        rgb = f"rgb({r},{g},{b})"
        colors_plotly.append(rgb)
    for node in G:
        try:
            color_map_plotly.append(colors_plotly[node_colors.loc[node].values[0]])
        except:
            color_map_plotly.append(colors_plotly[13])

    G_spring = nx.spring_layout(G)
    for edge in G.edges():
        x0, y0 = G_spring[edge[0]]
        x1, y1 = G_spring[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G_spring[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            size=10,
            line_width=2)
    )
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        try:
            author = list(G.nodes())[node]
            node_text.append(f'Author: {author}, Topic: {topic_per_author.loc[author].values[0]}, # of connections: '+str(len(adjacencies[1])))
        except KeyError:
            author = list(G.nodes())[node]
            node_text.append(f'Author: {author}, # of connections: '+str(len(adjacencies[1])))

    node_trace.marker.color = color_map_plotly
    node_trace.text = node_text
    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Co-Authorship Networks',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text='',
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig


@app.callback(
    dash.dependencies.Output('supply_graph', 'figure'),
    [dash.dependencies.Input('partner_type', 'value')]
)
def update_supplier_graph(partner_type):
    partners_df = pd.read_csv('data/processed/supply_chain_data.csv')
    partners_df.loc[partners_df['Country'].isin(['UNITED STATES', ' UNITED STATES ']), 'Country'] = 'US'
    partners_df.loc[partners_df['Country'].isin(['TAIWAN', ' TAIWAN ']), 'Country'] = 'Taiwan'
    if partner_type == 'Customer':
        customers_df = partners_df[partners_df['Relationship Type'] == 'Customer']
        G_customer = nx.from_pandas_edgelist(customers_df, source='Company', target='Partner', create_using=nx.DiGraph())
        return build_supply_chain(G_customer, customers_df, 'Customer')

    else:
        suppliers_df = partners_df[partners_df['Relationship Type'] == 'Supplier']
        G_supplier = nx.from_pandas_edgelist(suppliers_df, source='Company', target='Partner', create_using=nx.DiGraph())
        return build_supply_chain(G_supplier, suppliers_df, 'Supplier')




@app.callback(
    dash.dependencies.Output('centrality_authors', 'data'),
    [dash.dependencies.Input('topics-dropdown', 'value')],
)
def update_sku_ts(topics_dropdown):
     centrality_df = pd.read_csv("data/processed/author_centrality.csv")
     topic_df = centrality_df[centrality_df['Topic-Words'] == topics_dropdown]
     return topic_df.to_dict('records')

@app.callback(
     dash.dependencies.Output('choke_df', 'data'),
     [dash.dependencies.Input('partner_type', 'value'), dash.dependencies.Input('choke_type', 'value')],
 )
def update_centrality_table(partner, choke_type):
    if partner == 'Customer' and choke_type == 'Degree Centrality':
        df = pd.read_csv('data/processed/Customer_Outdegree_Score.csv')
    elif partner == 'Customer' and choke_type == 'Betweeness':
        df = pd.read_csv('data/processed/Customer_Betweeness_Score.csv')
    elif partner == 'Supplier' and choke_type == 'Degree Centrality':
        df = pd.read_csv('data/processed/Supplier_Indegree_Score.csv')
    else:
        df = pd.read_csv('data/processed/Supplier_Betweeness_Score.csv')
    df = df[df['Chokepoint Score'] > 0]
    df['Chokepoint Score'] =  df['Chokepoint Score'] / df['Chokepoint Score'].sum()
    return df.to_dict('records')

def build_topic_evolution():
    topic_evol_df = pd.read_csv('data/processed/topic_labels.csv')
    fig = px.line(topic_evol_df, x="date", y=topic_evol_df.columns, hover_data={"date": "|%B %d, %Y"}, title='HPC Topic Evolution: 2010-2021 (~10K Papers)')
    return fig

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

def build_supply_chain(G, partner_df, partner):
    country_colors = {'Taiwan': "Red", "US": 'Blue', "NETHERLANDS": 'Orange', "SWITZERLAND": "Pink"}
    color_map = []
    for node in G:
        try:
            country = partner_df.loc[partner_df['Company'] == node, 'Country'].unique()[0]
            color_map.append(country_colors[country])
        except IndexError:
            color_map.append('Black')

    G_spring = nx.spring_layout(G)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G_spring[edge[0]]
        x1, y1 = G_spring[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)


    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G_spring[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            size=10,
            line_width=2)
    )

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(list(G.nodes())[node])


    node_trace.marker.color = color_map
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout= go.Layout(
                        title=f"{partner} Networks",
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[dict(
                            text='',
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002 ) ],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)