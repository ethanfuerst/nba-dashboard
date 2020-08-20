#%%
import pandas as pd
from nba_season import NBA_Season
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, playercareerstats, shotchartdetail, leaguegamelog, shotchartlineupdetail,leaguestandings

#%%
season = NBA_Season()

#%%
df = season.game_log
df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])

bub = df[df['GAME_DATE'] > '2020-5-1']
bubble_teams = set(bub['TEAM_ABBREVIATION'])
df[['t1', 't2']] = df['MATCHUP'].str.split(' .* ',expand=True)
# - just the games for teams in the bubble playing teams in the bubble
df = df[df['t1'].isin(bubble_teams) & df['t2'].isin(bubble_teams)]

# - create method and use for each 
# - win, loss, percent
w_l = df.groupby(['TEAM_ABBREVIATION', 'WL']).size().unstack(fill_value=0).reset_index()
w_l['pct'] = w_l['W'] / (w_l['W'] + w_l['L'])
w_l = w_l.sort_values('pct', ascending=False)
# - games behind
w_l[['w_above', 'l_above']] = w_l[['W', 'L']].shift(1)
w_l['games behind'] = ((w_l['w_above'] - w_l['l_above']) - (w_l['W'] - w_l['L']))/2
w_l['games behind'] = w_l['games behind'].cumsum()


# %%
log = leaguestandings.LeagueStandings(league_id='00', season='2019', season_type='Regular Season')
df = log.get_data_frames()[0]
df['WinPCT'] = df['WinPCT'] * 100

# - whole league
total = df[['LeagueRank', 'TeamCity', 'TeamName', 'Record', 'WinPCT', 'HOME', 
            'ROAD', 'L10', 'ClinchIndicator']].sort_values(by=['LeagueRank', 'WinPCT'], ascending=[True, False])

# - conferences
east = df[df['Conference'] == 'East']
west = df[df['Conference'] == 'West']
east = east[['PlayoffRank', 'TeamCity', 'TeamName', 'Record', 'ConferenceGamesBack', 
            'ConferenceRecord', 'vsWest', 'WinPCT']].sort_values(by=['PlayoffRank', 
            'WinPCT'], ascending=[True, False])
west = west[['PlayoffRank', 'TeamCity', 'TeamName', 'Record', 'ConferenceGamesBack', 
            'ConferenceRecord', 'vsEast', 'WinPCT']].sort_values(by=['PlayoffRank', 
            'WinPCT'], ascending=[True, False])

# - divisions
atl = df[df['Division'] == 'Atlantic']
atl = atl[['DivisionRank', 'TeamCity', 'TeamName', 'Record', 'WinPCT', 'DivisionGamesBack', 
            'DivisionRecord', 'ClinchIndicator']].sort_values(by=['DivisionRank', 
            'WinPCT'], ascending=[True, False])
cen = df[df['Division'] == 'Central']
cen = cen[['DivisionRank', 'TeamCity', 'TeamName', 'Record', 'WinPCT', 'DivisionGamesBack', 
            'DivisionRecord', 'ClinchIndicator']].sort_values(by=['DivisionRank', 
            'WinPCT'], ascending=[True, False])
se = df[df['Division'] == 'Southeast']
se = se[['DivisionRank', 'TeamCity', 'TeamName', 'Record', 'WinPCT', 'DivisionGamesBack', 
            'DivisionRecord', 'ClinchIndicator']].sort_values(by=['DivisionRank', 
            'WinPCT'], ascending=[True, False])
nw = df[df['Division'] == 'Northwest']
nw = nw[['DivisionRank', 'TeamCity', 'TeamName', 'Record', 'WinPCT', 'DivisionGamesBack', 
            'DivisionRecord', 'ClinchIndicator']].sort_values(by=['DivisionRank', 
            'WinPCT'], ascending=[True, False])
pac = df[df['Division'] == 'Northwest']
pac = pac[['DivisionRank', 'TeamCity', 'TeamName', 'Record', 'WinPCT', 'DivisionGamesBack', 
            'DivisionRecord', 'ClinchIndicator']].sort_values(by=['DivisionRank', 
            'WinPCT'], ascending=[True, False])
sw = df[df['Division'] == 'Southwest']
sw = sw[['DivisionRank', 'TeamCity', 'TeamName', 'Record', 'WinPCT', 'DivisionGamesBack', 
            'DivisionRecord', 'ClinchIndicator']].sort_values(by=['DivisionRank', 
            'WinPCT'], ascending=[True, False])

# - streaks 
streaks = df[['LeagueRank', 'WinPCT', 'TeamCity', 'TeamName', 'Record', 'strLongHomeStreak', 
            'strLongRoadStreak', 'LongWinStreak', 'LongLossStreak', 'strCurrentHomeStreak', 
            'strCurrentRoadStreak']].sort_values(by=['LeagueRank', 'WinPCT'], ascending=[True, False])
streaks = streaks[['TeamCity', 'TeamName', 'Record', 'strLongHomeStreak', 'strLongRoadStreak', 
            'LongWinStreak', 'LongLossStreak', 'strCurrentHomeStreak', 'strCurrentRoadStreak']]

# - other
other = df[['LeagueRank', 'WinPCT', 'TeamCity', 'TeamName', 'Record', 'AheadAtHalf', 
            'BehindAtHalf', 'TiedAtHalf', 'Score100PTS', 'OppScore100PTS', 'OppOver500', 
            'FewerTurnovers']].sort_values(by=['LeagueRank', 'WinPCT'], ascending=[True, False])
other = other[['TeamCity', 'TeamName', 'Record', 'AheadAtHalf', 'BehindAtHalf', 
            'TiedAtHalf', 'Score100PTS', 'OppScore100PTS', 'OppOver500', 'FewerTurnovers']]

# - advanced
# - 2/3pt% (shot and allowed)
# - total +/-

# %%
df = season.reg_player_scoring
team_shots = df.groupby('TEAM_NAME').sum().reset_index()[['TEAM_NAME', 'FGM', 'FGA', 'FG3M', 'FG3A']]

# - get top 10 players and create line chart of scoring for them over games played
log = leagueleaders.LeagueLeaders(league_id=00, per_mode48='PerGame', scope='S', season='2019-20', season_type_all_star='Regular Season', stat_category_abbreviation='Points')




#%%

# - +/- for a team over time


