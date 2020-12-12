import numpy as np
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, playercareerstats, shotchartdetail, leaguegamelog, shotchartlineupdetail, leaguestandings, leagueleaders
from dashboard_reference import team_colors


def conf_table_data(season):
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

    return east, west

def scatter_data(season):
    html = requests.get('http://www.basketball-reference.com/leagues/NBA_{}.html'.format(season + 1)).content
    cleaned_soup = BeautifulSoup(re.sub(rb"<!--|-->",rb"", html), features='lxml')
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

    return df.drop(['Rank', 'Arena'], axis=1).copy()

