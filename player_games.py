#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nba_player import NBA_Player

#%%
df = NBA_Player('luka doncic').get_season(2019)

df['PPFTA'] = df['FT_PCT'].copy()
df['PPFGA'] = df['FG_PCT'] * 2
df['PP3PA'] = df['FG3_PCT'] * 3

df = df[['GAME_DATE', 'PPFTA', 'PPFGA', 'PP3PA']].copy()

df = df.rolling(window=3).mean().copy()

df.plot()

df[(df['PPFTA'] <= df['PPFGA']) & (df['PPFGA'] <= df['PP3PA'])]

#%%
df = NBA_Player('james harden').get_season(2019)

df['PPFTA'] = df['FT_PCT'].copy()
df['PPFGA'] = df['FG_PCT'] * 2
df['PP3PA'] = df['FG3_PCT'] * 3

df = df[['GAME_DATE', 'PPFTA', 'PPFGA', 'PP3PA']].copy()

df = df.rolling(window=3).mean().copy()

df.plot()

df[(df['PPFTA'] <= df['PPFGA']) & (df['PPFGA'] <= df['PP3PA'])]

# %%
# See where ppfta =< ppfga =< pp3pa
# Count games where above is true
