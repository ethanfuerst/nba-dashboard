#%%
import pandas as pd
import math
from nba_season import NBA_Season
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, playercareerstats, shotchartdetail, leaguegamelog, shotchartlineupdetail,leaguestandings
import plotly.graph_objects as go

#%%
log = leaguegamelog.LeagueGameLog(counter=0, direction='ASC', league_id='00', 
                player_or_team_abbreviation='T', season='2019-20', season_type_all_star='Regular Season')
df = log.get_data_frames()[0]

bubble_teams = set(df[pd.to_datetime(df['GAME_DATE']) > '2020-5-1']['TEAM_ABBREVIATION'])
df = df[df['TEAM_ABBREVIATION'].isin(bubble_teams)]
pre_bubble = df[pd.to_datetime(df['GAME_DATE']) < '2020-5-1']
pre_bubb_stats = pre_bubble.groupby('TEAM_NAME').sum().reset_index()[['TEAM_NAME', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA']]
pre_bubb_stats['FG%'] = round(round(pre_bubb_stats['FGM'] / pre_bubb_stats['FGA'],4) * 100,2)
pre_bubb_stats['3%'] = round(round(pre_bubb_stats['FG3M'] / pre_bubb_stats['FG3A'],4) * 100,2)
pre_bubb_stats['FT%'] = round(round(pre_bubb_stats['FTM'] / pre_bubb_stats['FTA'],4) * 100,2)
pre_bubb_stats = pre_bubb_stats[['TEAM_NAME', 'FG%', '3%', 'FT%']]

bubble = df[pd.to_datetime(df['GAME_DATE']) > '2020-5-1']
bubb_stats = bubble.groupby('TEAM_NAME').sum().reset_index()[['TEAM_NAME', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA']]
bubb_stats['FG%'] = round(round(bubb_stats['FGM'] / bubb_stats['FGA'],4) * 100,2)
bubb_stats['3%'] = round(round(bubb_stats['FG3M'] / bubb_stats['FG3A'],4) * 100,2)
bubb_stats['FT%'] = round(round(bubb_stats['FTM'] / bubb_stats['FTA'],4) * 100,2)
bubb_stats = bubb_stats[['TEAM_NAME', 'FG%', '3%', 'FT%']]

df = pd.merge(left=pre_bubb_stats, right=bubb_stats, how='inner', on='TEAM_NAME', suffixes=('_pre', '_dur'))
df['fg diff'] = df['FG%_pre'] - df['FG%_dur']
df['3 diff'] = df['3%_pre'] - df['3%_dur']
df['ft diff'] = df['FT%_pre'] - df['FT%_dur']
# %%
# todo add filter toggle
df = df.sort_values('fg diff', ascending=False)
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['FG%_pre'],
    y=df['TEAM_NAME'],
    marker=dict(color="orange", size=12),
    mode="markers",
    name="Pre-bubble",
    hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' shot %{x}% from 2 before the bubble<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=df['FG%_dur'],
    y=df['TEAM_NAME'],
    marker=dict(color="blue", size=12),
    mode="markers",
    name="Bubble",
    hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' shot %{x}% from 2 in the bubble<extra></extra>'
))

fig.update_layout(title="Pre-bubble shooting vs. bubble shooting",
                  xaxis_title="FG%",
                  yaxis_title="Team",
                  width=850,
                  height=850
                  )

fig.show()
# %%
