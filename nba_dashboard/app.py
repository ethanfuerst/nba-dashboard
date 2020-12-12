import dash
import dash_core_components as dcc
import dash_html_components as html
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
    html.Div([
        html.Div([dcc.Graph(id='g1', figure=conf_table(east))], className="column"),
        html.Div([dcc.Graph(id='g2', figure=conf_table(west))], className="column")
    ], className="row"),
    dcc.Graph()
])


if __name__ == '__main__':
    app.run_server(debug=True)
