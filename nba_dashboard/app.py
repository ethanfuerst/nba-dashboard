import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import sys
from datetime import datetime
from nba_data import scatter_data, conf_table_data, team_colors, scatter_vals, conf_table_cols
from table_styles import conf_table_params, center_style

def conf_table(conf_df):
    data = go.Table(
        header=dict(
            values=['<b>Rank</b>'] + [f'<b>{i}</b>' for i in conf_df.columns],
            line_color='black',
            font_color='black',
            fill_color='lightgrey',
            align='center'
        ),
        cells=dict(
            values=[[f'<b>{i}</b>' for i in range(1,9)] 
                    + [str(i) for i in range(9,16)]] 
                    + [conf_df[k].tolist() for k in conf_df.columns[:]],
            align = "left",
            fill_color=[['#E6E6E6'] * 15, [team_colors[i][0] for i in playoff_splitter(conf_df)]] + [['#E6E6E6'] * 15] * 6,
            line_color=[['#FFFFFF'] * 15, [team_colors[i][1] for i in playoff_splitter(conf_df)]] + [['#FFFFFF'] * 15] * 6,
            font_color=[['#000000'] * 15, ['#FFFFFF'] * 15] + [['#000000'] * 15] * 10 + 
                        [['#238823' if float(i) > 0 else '#FF0000' if float(i) < 0 else '#000000' for i in conf_df['Difference'].values]] + 
                        [['#000000'] * 15] * 2,
            height=45
        )
    )

    layout = dict(
        showlegend=False,
        title_text=f"{conf_df.name} Conference",
        height=1060
    )

    return dict(
        data=[data], 
        layout=layout
    )

playoff_splitter = lambda x: [j.rsplit(' -')[0] for j in x['Team'].values]

#! dynamically pull from the data
show_playoff_markers = False

playoff_markers = [
    html.H2('Conference clinched: -z'),
    html.H2('Division clinched: - y'),
    html.H2('Playoff spot clinched: - x'),
    html.H2('Missed Playoffs: - e')] if show_playoff_markers else []


app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server
app.layout = html.Div([
    dbc.Row(
        html.H1(
            children='NBA Regular Season Dashboard',
            style=center_style)
        ),
    html.Div([
        dcc.Dropdown(
            id='season_val',
            options=[{'label': str(i) + "-" + str(i + 1)[2:] + ' Season', 'value': i} for i in range(2012,2021)],
            value='2020'
        )
    ], 
    style={
        'width': '20%',
        'padding-left':'40%',
        'padding-right':'40%', 
        'textAlign': 'center'
    }),
    
    dbc.Row(
        html.H2(
            children=f'Last Updated: {datetime.now().strftime("%-I:%M:%S %p")} CST',
            style=center_style
        )
    ),
    html.Br(),

    dbc.Row(
        html.H1(
            children='Western Conference Standings',
            style=center_style
        )
    ),
    dbc.Row(
        children=playoff_markers,
        style=center_style
    ),
    html.Center([
        html.Div([
            dt.DataTable(
                id='west_table',
                columns=[{"name": i, "id": i} for i in conf_table_cols('West')],
                **conf_table_params
            )
        ])
    ]),

    dbc.Row(
        html.H1(
            children='Eastern Conference Standings',
            style=center_style
        )
    ),
    dbc.Row(
        children=playoff_markers,
        style=center_style
    ),
    html.Center([
        html.Div([
            dt.DataTable(
                id='east_table',
                columns=[{"name": i, "id": i} for i in conf_table_cols('East')],
                **conf_table_params
            )
        ])
    ]),

    dbc.Row(
        html.H1(
            children='League Statistics Comparison',
            style=center_style
        )
    ),
    dbc.Row(
        children=[html.H2('Choose two metrics to compare how the league stacks up!')],
        style=center_style
    ),
    html.Center(
        [dcc.Graph(id='scatter1')]
    ),

    html.Div([
        dcc.Dropdown(
                id='scatter1-x',
                options=[{'label': i, 'value': i} for i in scatter_vals[1:]],
                value='Offensive Rating'
        )
    ],
    style={
        'width': '25%',
        'padding-left':'25%',
        'display': 'inline-block',
        'textAlign': 'center'
    }),

    html.Div([
        dcc.Dropdown(
            id='scatter1-y',
            options=[{'label': i, 'value': i} for i in scatter_vals[1:]],
            value='Defensive Rating'
        )
    ],
    style={
        'width': '25%',
        'padding-right':'25%',
        'float': 'right',
        'display': 'inline-block',
        'textAlign': 'center'
    }),

    dbc.Row(
        html.H1(
            children='League Standings',
            style=center_style
        )
    ),
    dbc.Row(
        children=playoff_markers,
        style=center_style
    ),
    html.Center([
        html.Div([
            dt.DataTable(
                id='league_table',
                columns=[{"name": i, "id": i} for i in conf_table_cols('Conference')],
                **conf_table_params
            )
        ])
    ]),
])


@app.callback(Output('east_table', 'data'),
    [Input('season_val', 'value')])
def update_east_table(season_val):
    east = conf_table_data(season=season_val, conference='East')
    return east.to_dict('rows')

@app.callback(Output('west_table', 'data'),
    [Input('season_val', 'value')])
def update_west_table(season_val):
    west = conf_table_data(season=season_val, conference='West')

    return west.to_dict('rows')

@app.callback(Output('league_table', 'data'),
    [Input('season_val', 'value')])
def update_league_table(season_val):
    league = conf_table_data(season=season_val, conference='League')

    return league.to_dict('rows')

@app.callback(Output('scatter1', 'figure'),
              [Input('season_val', 'value'),
              Input('scatter1-x', 'value'),
              Input('scatter1-y', 'value')])
def update_scatter1(season_val, x, y):
    scatter_df = scatter_data(season_val)
    
    scatter_to_flip = ['Defensive Rating', 'Turnover Percentage', 
                        'Effective Field Goal Percentage Allowed', 
                        'Opponent Free Throws Per Field Goal Attempt']

    return {
        'data': [
            go.Scatter(
                x=scatter_df[x],
                y=scatter_df[y], 
                mode='markers',
                marker=dict(color=[team_colors[i][0] for i in playoff_splitter(scatter_df)],
                    size=12,
                    line=dict(
                        width=3,
                        color=[team_colors[i][1] for i in playoff_splitter(scatter_df)]
                    )
                ),
                hovertemplate=
                    scatter_df['Team'].astype(str)+
                    f'<br><b>{x}</b>: ' + scatter_df[x].astype(str) +'<br>'+
                    f'<b>{y}</b>: ' + scatter_df[y].astype(str) +'<br>'+
                    '<extra></extra>'
            )
        ],
        'layout': go.Layout(
            plot_bgcolor='#e6e6e6',
            height=750,
            width=750,
            showlegend=False,
            xaxis=dict(
                title=x,
                autorange='reversed' if x in scatter_to_flip else True
            ),
            yaxis=dict(
                title=y,
                autorange='reversed' if y in scatter_to_flip else True
            ),
            hovermode="closest",
            shapes=[
                dict(
                    type='line',
                    x0=scatter_df[x].mean(),
                    y0=scatter_df[y].min() - ((scatter_df[y].max() - scatter_df[y].min()) * (1/15)),
                    x1=scatter_df[x].mean(),
                    y1=scatter_df[y].max() + ((scatter_df[y].max() - scatter_df[y].min()) * (1/15)),
                    line=dict(
                        color='black',
                        width=2
                    )
                ),
                dict(type='line',
                    x0=scatter_df[x].min() - ((scatter_df[x].max() - scatter_df[x].min()) * (1/15)),
                    y0=scatter_df[y].mean(),
                    x1=scatter_df[x].max() + ((scatter_df[x].max() - scatter_df[x].min()) * (1/15)),
                    y1=scatter_df[y].mean(),
                    line=dict(
                        color='black',
                        width=2
                    )
                )
            ]
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
