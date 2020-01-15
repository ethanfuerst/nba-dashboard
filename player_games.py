#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playergamelog

#%%
# nba_api
player_id = players.find_players_by_full_name('luka doncic')[0]['id']
player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)

# Figure out how I want to do by season and playoffs and whatnot
# For now, just get most recent season
log = playergamelog.PlayerGameLog(player_id=player_id, season=2019, season_type_all_star='Regular Season')
df = log.get_data_frames()[0]

# df['PPFTA'] = df['FT_PCT'].copy()
df['PPFGA'] = df['FG_PCT'] * 2
df['PP3PA'] = df['FG3_PCT'] * 3

# Moving average of 3? 5?