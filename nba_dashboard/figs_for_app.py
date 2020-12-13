#%%
import pandas as pd
import plotly.graph_objects as go
import requests
import re
from bs4 import BeautifulSoup
from nba_api.stats.endpoints import leaguegamelog, leaguestandings, leagueleaders, leaguedashteamstats
from dashboard_reference import team_colors


season = 2019

# - advanced
# - 2/3pt% (shot and allowed)
# - total +/-
# - +/- for a team over time

# %%
log = leaguegamelog.LeagueGameLog(counter=0, direction='ASC', league_id='00', 
                player_or_team_abbreviation='P', season=season, season_type_all_star='Regular Season')
df = log.get_data_frames()[0]
team_shots = df.groupby('TEAM_NAME').sum().reset_index()[['TEAM_NAME', 'FGM', 'FGA', 'FG3M', 'FG3A']]


#%%
# - get top 10 players and create line chart of scoring for them over games played
#! error pulling this
log = leagueleaders.LeagueLeaders(league_id='00', per_mode48='PerGame', scope='S', season=season, season_type_all_star='Regular Season', stat_category_abbreviation='Points')
