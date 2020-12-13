import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, playercareerstats, shotchartdetail, leaguegamelog, shotchartlineupdetail, leaguestandings, leagueleaders
from dashboard_reference import team_colors
from nba_data import scatter_data, conf_table_data


app = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

season = 2019

east, west = conf_table_data(2019)
scatter_df = scatter_data(2019)
scatter_vals = scatter_df.columns.to_list()[1:]

def conf_table(conf_df):
    data = go.Table(
        header=dict(
            values=['<b>{}</b>'.format(i) for i in conf_df.columns],
            line_color='black',
            font_color='black',
            fill_color='lightgrey',
            align='center'
        ),
        cells=dict(
            values=[['<b>{}</b>'.format(i) for i in range(1,9)] 
                    + [str(i) for i in range(9,16)]] 
                    + [conf_df[k].tolist() for k in conf_df.columns[1:]],
            align = "left",
            fill_color=[['#E6E6E6'] * 15, [team_colors[i][0] for i in conf_df['Team'].values]] + [['#E6E6E6'] * 15] * 6,
            line_color=[['#FFFFFF'] * 15, [team_colors[i][1] for i in conf_df['Team'].values]] + [['#FFFFFF'] * 15] * 6,
            font_color=[['#000000'] * 15, ['#FFFFFF'] * 15] + [['#000000'] * 15] * 6,
            height=45
            )
    )

    layout = dict(
        showlegend=False,
        title_text="{} Conference".format(conf_df.name),
        height=900
    )
    return dict(data=[data], layout=layout)

app = dash.Dash()
app.layout = html.Div([
    dbc.Row(html.H1(children='Western Conference Standings',
        style={
            'textAlign': 'center'
        })),
    dbc.Row(children=[html.H2('Conference clinched: -w'),
                    html.H2('Division clinched: - nw, p, sw'),
                    html.H2('Playoff spot clinched: - o'),
                    html.H2('Missed Playoffs: - x')],
        style={
            'textAlign': 'center'
        }
        ),
    html.Div([dcc.Graph(id='g1', figure=conf_table(west))]),
    dbc.Row(html.H1(children='Eastern Conference Standings',
        style={
            'textAlign': 'center'
        })),
        dbc.Row(children=[html.H2('Conference clinched: -w'),
                    html.H2('Division clinched: - se, c, a'),
                    html.H2('Playoff spot clinched: - o'),
                    html.H2('Missed Playoffs: - x')],
        style={
            'textAlign': 'center'
        }
        ),
    html.Div([dcc.Graph(id='g2', figure=conf_table(east))]),
    dcc.Graph(id='scatter1'),
    html.Div([
            dcc.Dropdown(
                id='scatter1-x',
                options=[{'label': i, 'value': i} for i in scatter_vals],
                value='Offensive Rating'
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Dropdown(
            id='scatter1-y',
            options=[{'label': i, 'value': i} for i in scatter_vals],
            value='Wins'
        )
    ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
])

@app.callback(Output('scatter1', 'figure'),
              [Input('scatter1-x', 'value'),
              Input('scatter1-y', 'value')])
def update_scatter2(x, y):

    return {
        'data': [go.Scatter(x=scatter_df[x],
                    y=scatter_df[y], 
                    mode='markers',
                    marker=dict(color=[team_colors[i][0] for i in scatter_df['Team'].values],
                        size=12,
                        line=dict(width=2,
                                        color=[team_colors[i][1] for i in scatter_df['Team'].values])
                    ),
                    hovertemplate=scatter_df['Team'].astype(str)+
                        '<br><b>{}</b>: '.format(x)+ scatter_df[x].astype(str) +'<br>'+
                        '<b>{}</b>: '.format(y)+ scatter_df[y].astype(str) +'<br>'+
                        '<extra></extra>'
                )
        ],
        'layout': go.Layout(
            plot_bgcolor='#e6e6e6',
            height=800,
            width=800,
            showlegend=False,
            xaxis=dict(
                title=x
            ),
            yaxis=dict(
                title=y
            ),
            hovermode="closest"
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
