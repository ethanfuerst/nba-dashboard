#%%
import pandas as pd
import plotly.graph_objects as go
import requests
import re
from bs4 import BeautifulSoup
from plotly.subplots import make_subplots
from nba_api.stats.endpoints import leaguegamelog, leaguestandings, leagueleaders, leaguedashteamstats
from dashboard_reference import team_colors

season = 2019

# %%
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
east.name = 'East'
west.name = 'West'

#%%
for conf in [east, west]:
    fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>{}</b>'.format(i) for i in conf.columns],
                line_color='black',
                font_color='black',
                fill_color='lightgrey',
                align='center'
            ),
            cells=dict(
                values=[['<b>{}</b>'.format(i) for i in range(1,9)] 
                        + [str(i) for i in range(9,16)]] 
                        + [conf[k].tolist() for k in conf.columns[1:]],
                align = "left",
                fill_color=[['#E6E6E6'] * 15, [team_colors[i][0] for i in conf['Team'].values]] + [['#E6E6E6'] * 15] * 6,
                line_color=[['#FFFFFF'] * 15, [team_colors[i][1] for i in conf['Team'].values]] + [['#FFFFFF'] * 15] * 6,
                font_color=[['#000000'] * 15, ['#FFFFFF'] * 15] + [['#000000'] * 15] * 6,
                height=45
                )
        )
    ])

    fig.update_layout(
        height=950,
        width=900,
        showlegend=False,
        title_text="{} Conference".format(conf.name)
    )

    fig.show()

#%%

# - streaks 
streaks = df[['LeagueRank', 'WinPCT', 'Team', 'Record', 'strLongHomeStreak', 
            'strLongRoadStreak', 'LongWinStreak', 'LongLossStreak', 'strCurrentHomeStreak', 
            'strCurrentRoadStreak']].sort_values(by=['LeagueRank', 'WinPCT'], ascending=[True, False])
streaks = streaks[['Team', 'Record', 'strLongHomeStreak', 'strLongRoadStreak', 
            'LongWinStreak', 'LongLossStreak', 'strCurrentHomeStreak', 'strCurrentRoadStreak']]
streaks.name = "Streaks"

# - other
other = df[['LeagueRank', 'WinPCT', 'Team', 'Record', 'AheadAtHalf', 
            'BehindAtHalf', 'TiedAtHalf', 'Score100PTS', 'OppScore100PTS', 'OppOver500', 
            'FewerTurnovers']].sort_values(by=['LeagueRank', 'WinPCT'], ascending=[True, False])
other = other[['Team', 'Record', 'AheadAtHalf', 'BehindAtHalf', 
            'TiedAtHalf', 'Score100PTS', 'OppScore100PTS', 'OppOver500', 'FewerTurnovers']]
other.name = "Other"

for data in [streaks, other]:
    fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>{}</b>'.format(i) for i in data.columns[:]],
                line_color='black',
                font_color='black',
                fill_color='lightgrey',
                align='center'
            ),
            cells=dict(
                values=[data[k].tolist() for k in data.columns[:]],
                align = "left",
                fill_color=[[team_colors[i][0] for i in data['Team'].values], ['#E6E6E6'] * 15] + [['#E6E6E6'] * 15] * 6,
                line_color=[[team_colors[i][1] for i in data['Team'].values], ['#FFFFFF'] * 15] + [['#FFFFFF'] * 15] * 6,
                font_color=[['#FFFFFF'] * 15, ['#000000'] * 15] + [['#000000'] * 15] * 6,
                height=45
                )
        )
    ])

    fig.update_layout(
        height=950,
        width=900,
        showlegend=False,
        title_text=data.name
    )

    fig.show()

#%%
# log = leaguedashteamstats.LeagueDashTeamStats(last_n_games=100,
# season=season, measure_type_detailed_defense='Base')
# df = log.get_data_frames()[0]

html = requests.get("http://www.basketball-reference.com/leagues/NBA_{}.html".format(season + 1)).content
cleaned_soup = BeautifulSoup(re.sub(rb"<!--|-->",rb"", html))
misc_table = cleaned_soup.find('table', {'id':'misc_stats'})

df = pd.read_html(str(misc_table))[0]
df.columns = df.columns.get_level_values(1)
df['Team'] = df['Team'].apply(lambda x: x if x[-1] != '*' else x[:-1])

df.columns = ['Rank', 'Team', 'Average Age', 'Wins', 'Losses', 'Pythagorean Wins', 'Pythagorean Losses', 
            'Margin of Victory', 'Strength of Schedule', 'Simple Rating System', 'Offensive Rating', 
            'Defensive Rating', 'Net Rating', 'Pace', 'Free Throw Attempt Rate', '3 Point Attempt Rate', 
            'True Shooting Percentage', 'Effective Field Goal Percentage', 'Turnover Percentage', 
            'Offensive Rebound Percentage', 'Free Throws Per Field Goal Attempt', 
            'Effective Field Goal Percentage Allowed', 'Opponent Turnover Percentage', 
            'Defensive Rebound Pecentage', 'Opponent Free Throws Per Field Goal Attempt', 'Arena', 'Attendance', 
            'Attendance Per Game']
df = df[df['Team'] != 'League Average']
df[['Wins', 'Losses']] = df[['Wins', 'Losses']].astype(int)

df = df.drop(['Rank', 'Arena'], axis=1).copy()

# for i in ['opponent', 'team']:
#     html_table = cleaned_soup.find('table', {'id':'{}-stats-per_poss'.format(i)})

#     table = pd.read_html(str(html_table))[0]
#     table = table[['Team', 'PTS']].copy()
#     table['Team'] = table['Team'].apply(lambda x: x if x[-1] != '*' else x[:-1])

#     if i == 'opponent':
#         table.columns = ['Team', 'Defensive Efficiency']
#     else:
#         table.columns = ['Team', 'Offensive Efficiency']
    
#     df = df.merge(table, left_on='Team', right_on='Team', suffixes=('', '')).copy()

#%%

x = 'Wins'
y = 'Attendance Per Game'

#! make markers bigger and add outline
fig = go.Figure(data=[
    go.Scatter(x=df[x],
                y=df[y], 
                mode='markers',
                marker=dict(color=[team_colors[i][0] for i in df['Team'].values],
                    size=10
                ),
                hovertemplate=df['Team'].astype(str)+
                    '<br><b>{}</b>: '.format(x)+ df[x].astype(str) +'<br>'+
                    '<b>{}</b>: '.format(y)+ df[y].astype(str) +'<br>'+
                    '<extra></extra>'
            )
    ]
)

fig.update_layout(
        height=800,
        width=800,
        showlegend=False,
        xaxis=dict(
            title=x
        ),
        yaxis=dict(
            title=y
        )
    )

fig.show()


#%%

# - advanced
# - 2/3pt% (shot and allowed)
# - total +/-

# %%
log = leaguegamelog.LeagueGameLog(counter=0, direction='ASC', league_id='00', 
                player_or_team_abbreviation='P', season=season, season_type_all_star='Regular Season')
df = log.get_data_frames()[0]
team_shots = df.groupby('TEAM_NAME').sum().reset_index()[['TEAM_NAME', 'FGM', 'FGA', 'FG3M', 'FG3A']]


#%%
# - get top 10 players and create line chart of scoring for them over games played
#! error pulling this
log = leagueleaders.LeagueLeaders(league_id='00', per_mode48='PerGame', scope='S', season=season, season_type_all_star='Regular Season', stat_category_abbreviation='Points')




#%%

# - +/- for a team over time

