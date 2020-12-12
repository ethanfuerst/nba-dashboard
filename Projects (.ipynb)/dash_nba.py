import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, playercareerstats, shotchartdetail, leaguegamelog, shotchartlineupdetail, leaguestandings, leagueleaders
from dashboard_reference import team_colors

app = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

season = 2019

log = leaguestandings.LeagueStandings(league_id='00', season=str(season), season_type='Regular Season')
df = log.get_data_frames()[0]
df['WinPCT'] = round(df['WinPCT'] * 100, 2).astype(str) + '%'
df['TeamCity'] = df['TeamCity'].replace('LA', 'Los Angeles')
df['Team'] = df['TeamCity'] + ' ' + df['TeamName']

# - conferences
east = df[df['Conference'] == 'East']
west = df[df['Conference'] == 'West']
east = east[['PlayoffRank', 'Team', 'Record', 'ConferenceGamesBack', 
            'vsWest', 'ConferenceRecord', 'WinPCT', 'ClinchIndicator']].sort_values(by=['PlayoffRank', 
            'WinPCT'], ascending=[True, False])
west = west[['PlayoffRank', 'Team', 'Record', 'ConferenceGamesBack', 
            'ConferenceRecord', 'vsEast', 'WinPCT', 'ClinchIndicator']].sort_values(by=['PlayoffRank', 
            'WinPCT'], ascending=[True, False])
west.columns = east.columns = ['Rank', 'Team', 'Record', 'Games Back', 'vs. West', 'vs. East', 'Win %', 'Clinch Indicator']
west.name = 'West'
east.name = 'East'


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
        title_text="{} Conference".format(conf_df.name)
    )
    return dict(data=[data], layout=layout)


# - conferences
east = df[df['Conference'] == 'East']
west = df[df['Conference'] == 'West']
east = east[['PlayoffRank', 'Team', 'Record', 'ConferenceGamesBack', 
            'vsWest', 'ConferenceRecord', 'WinPCT']].sort_values(by=['PlayoffRank', 
            'WinPCT'], ascending=[True, False])
west = west[['PlayoffRank', 'Team', 'Record', 'ConferenceGamesBack', 
            'ConferenceRecord', 'vsEast', 'WinPCT']].sort_values(by=['PlayoffRank', 
            'WinPCT'], ascending=[True, False])
west.columns = east.columns = ['Rank', 'Team', 'Record', 'Games Back', 'vs. West', 'vs. East', 'Win %']
east.name = 'East'
west.name = 'West'

app = dash.Dash()
app.layout = html.Div([
    html.Div([
        html.Div([dcc.Graph(id='g1', figure=conf_table(east))], className="column"),
        html.Div([dcc.Graph(id='g2', figure=conf_table(west))], className="column")
    ], className="row")
])


if __name__ == '__main__':
    app.run_server(port=3005)
