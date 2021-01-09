import numpy as np
import pandas as pd
import requests
import re
import time
import os
from bs4 import BeautifulSoup
from nba_api.stats.endpoints import leaguestandings


def get_colors(teamname):
    if teamname == 'New Orleans Pelicans':
        teamname = 'New Orleans Pelicans Team'
    URL = f"https://teamcolorcodes.com/{teamname.replace(' ', '-').lower()}-color-codes/"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    colors = []
    for i in soup.find_all(class_='colorblock'):
        hex = re.compile(r'#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})(?=;|[^(]*\))').findall(i.text)
        if len(hex) > 0:
            colors.append(hex[0])

    if teamname == 'San Antonio Spurs':
        colors[0] = '#000000'
        colors[1] = '#C4CED4'
    return colors

# - use code below to regenerate team_colors
# log = leaguestandings.LeagueStandings(league_id='00', season='2019', season_type='Regular Season')
# df = log.get_data_frames()[0]
# df['Team'] = df['TeamCity'] + ' ' + df['TeamName']

# team_colors = {}
# for team in df['Team'].sort_values().values:
#     colors = get_colors(team)
#     team_colors.update({team: colors})

team_colors = {
    "Atlanta Hawks": ["#e03a3e", "#C1D32F", "#26282A", "#C8102E", "#FFCD00", "#87674F", "#000000"], 
    "Boston Celtics": ["#007A33", "#BA9653", "#963821", "#E59E6D", "#000000"], 
    "Brooklyn Nets": ["#000000", "#FFFFFF", "#002A60", "#CD1041", "#777D84", "#C6CFD4", "#FFFFFF"], 
    "Charlotte Bobcats": ["#2e5a8b", "#f26432", "#959da0", "#232020"],  
    "Charlotte Hornets": ["#1d1160", "#00788C", "#A1A1A4", "#00778B", "#280071", "#F9423A"], 
    "Chicago Bulls": ["#CE1141", "#000000"], 
    "Cleveland Cavaliers": ["#860038", "#041E42", "#FDBB30", "#000000", "#E35205", "#5C88DA", "#27251F", "#DC3B34", "#04225C", "#FFFFFF"], 
    "Dallas Mavericks": ["#00538C", "#B8C4CA", "#002B5E", "#000000", "#002855", "#00843D"], 
    "Denver Nuggets": ["#0E2240", "#FEC524", "#8B2131", "#1D428A", "#00285E", "#418FDE", "#FDB927", "#041E42", "#9D2235", "#8B6F4E"], 
    "Detroit Pistons": ["#C8102E", "#1d42ba", "#bec0c2", "#002D62", "#ED174C", "#006BB6", "#bec0c2", "#002D62", "#D50032", "#003DA5", "#041E42", "#9D2235", "#FFA300", "#006272", "#8A8D8F", "#000000"], 
    "Golden State Warriors": ["#1D428A", "#ffc72c", "#006BB6", "#FDB927", "#26282A", "#041E42", "#BE3A34", "#FFA300", "#00A9E0", "#FFCD00"], 
    "Houston Rockets": ["#CE1141", "#000000", "#C4CED4", "#041E42", "#2C7AA1", "#BA0C2F", "#8A8D8F", "#BA0C2F", "#000000", "#FFC72C"], 
    "Indiana Pacers": ["#002D62", "#FDBB30", "#BEC0C2"], 
    "Los Angeles Clippers": ["#c8102E", "#1d428a", "#BEC0C2", "#000000"], 
    "Los Angeles Lakers": ["#552583", "#FDB927", "#000000"], 
    "Memphis Grizzlies": ["#5D76A9", "#12173F", "#F5B112", "#707271", "#6189B9", "#00285E", "#FDB927", "#BED4E9", "#00B2A9", "#E43C40", "#BC7844", "#040204", "#FFFFFF"], 
    "Miami Heat": ["#98002E", "#F9A01B", "#000000", "#41B6E6", "#db3eb1", "#000000", "#FFFFFF", "#BA0C2F", "#FEDD00", "#000000"], 
    "Milwaukee Bucks": ["#00471B", "#D5C8AD", "#0077c0", "#000000", "#AC1a2f", "#274e37", "#95999d", "#FFFFFF", "#702F8A", "#2C5234", "#8A8D8F", "#009429", "#f7a500", "#FFFFFF", "#000000"], 
    "Minnesota Timberwolves": ["#0C2340", "#236192", "#9ea2a2", "#78BE20", "#221C35", "#981D97", "#FFFFFF", "#236192", "#00843D", "#8A8D8F", "#000000", "#FFD700", "#C8102E", "#24429C", "#1CA64C", "#848A8C", "#FFFFFF"], 
    "New Orleans Pelicans": ["#0C2340", "#C8102E", "#85714D"], 
    "New York Knicks": ["#006BB6", "#F58426", "#BEC0C2", "#000000", "#0072CE", "#FE5000", "#8A8D8F", "#000000"], 
    "Oklahoma City Thunder": ["#007ac1", "#ef3b24", "#002D62", "#fdbb30"], 
    "Orlando Magic": ["#0077c0", "#C4ced4", "#000000"], 
    "Philadelphia 76ers": ["#006bb6", "#ed174c", "#002B5C", "#c4ced4", "#006bb6", "#D50032", "#BB9754", "#040204", "#002F6C", "#D50032"], 
    "Phoenix Suns": ["#1d1160", "#e56020", "#000000", "#63727A", "#F9AD1B", "#B95915", "#Bec0c2", "#FF6900", "#FE5000", "#EF3340", "#5F259F", "#000000"], 
    "Portland Trail Blazers": ["#E03A3E", "#000000"], 
    "Sacramento Kings": ["#5a2d81", "#63727A", "#000000", "#542e91", "#c4ced4", "#000000"], 
    "San Antonio Spurs": ["#000000", "#C4CED4", "#8a8d8f", "#000000", "#EF426F", "#00B2A9", "#FF8200"], 
    "Toronto Raptors": ["#ce1141", "#000000", "#A1A1A4", "#B4975A", "#753BBD", "#BA0C2F", "#8A8D8F", "#000000"], 
    "Utah Jazz": ["#002B5C", "#F9A01B", "#F9A01B", "#00471B", "#3E2680", "#6CAEDF", "#753BBD", "#00A9E0", "#006272", "#954E4C"], 
    "Washington Wizards": ["#002B5C", "#e31837", "#C4CED4"]
    }

table_cols = ['Team', 'Record', 'Win %', 'Games Back', 'at Home', 'Away', 'vs. Division',  
                    'PPG', 'Opponent PPG', 'Difference', 'Current Streak', 'Last 10 Games']

def conf_table_cols(conference):

    cols = table_cols[:]
    cols.insert(7, f'vs. {conference}')
    
    return cols

def conf_table_data(season, conference):
    #! add in playoff string reading for previous years after this works for current year
    dfs = pd.read_html(f'https://www.espn.com/nba/standings/_/season/{int(season) + 1}')
    time.sleep(1)

    flatten = lambda t: [item for sublist in t for item in sublist]
    start_cols = ['Team', 'Record', 'PCT', 'GB', 'HOME', 'AWAY', 'DIV', 'CONF', 'PPG', 'OPP PPG',
            'DIFF', 'STRK', 'L10']
    
    if conference == 'West':
        val = 3
    else:
        val = 1

    conf = dfs[val]

    teams = pd.DataFrame([dfs[val - 1].columns.values.tolist()[0]] + flatten(dfs[val - 1].values.tolist()))
    def playoff_str(x):
        if str(x)[5].isdigit() and str(x)[6].islower():
            return str(x)[6:8]
        elif str(x)[5].islower():
            return str(x)[5:7]
        else:
            return ''

    playoff_str_vals = teams.apply(playoff_str, axis=1)
    teams = pd.DataFrame([item.split(' ')[-1] for sublist in teams.values for item in sublist])

    teams = teams.replace({0:{i.split(' ')[-1]: i for i in list(team_colors.keys())}})
    teams['t'] = playoff_str_vals
    teams = teams.apply(lambda row: row[0] + ' -' + row['t'] if row['t'] != '' else row[0], axis=1)

    conf['Team'] = teams.apply(lambda x: x[:-1] if x.endswith(' ') else x)
    conf['PCT'] = round(conf['PCT'] * 100, 2).astype(str) + '%'
    conf['Record'] = conf['W'].astype(str) + '-' + conf['L'].astype(str)

    for j in ['PPG', 'OPP PPG', 'DIFF']:
        conf[j] = round(conf[j], 1)
        conf[j] = conf[j].astype(str)
    
    conf = conf.reindex(columns=start_cols).copy()
    conf.columns = conf_table_cols(conference)

    return conf.copy()

conf_table_cond_styles = [{
                    'if': {
                        'column_id': 'Team',
                        'filter_query': '{Team} contains "' + team + '"'
                    },
                    'backgroundColor': background_color,
                    'border': '2px solid ' + trim_color,
                    'color': 'white'
                } for team, background_color, trim_color in zip(team_colors.keys(), 
                        [team_colors[d][0] for d in team_colors], 
                        [team_colors[d][1] for d in team_colors])] + [
                        {
                            'if': {
                                'filter_query': '{Difference} < 0.0',
                                'column_id': 'Difference'
                        },
                        'color': 'red'
                    },
                    {
                            'if': {
                                'filter_query': '{Difference} > 0.0',
                                'column_id': 'Difference'
                        },
                        'color': 'green'
                    }
                ]

scatter_vals = ['Team', 'Average Age', 'Wins', 'Losses', 'Pythagorean Wins', 'Pythagorean Losses', 
                'Margin of Victory', 'Strength of Schedule', 'Simple Rating System', 'Offensive Rating', 
                'Defensive Rating', 'Net Rating', 'Pace', 'Free Throw Attempt Rate', '3 Point Attempt Rate', 
                'True Shooting Percentage', 'Effective Field Goal Percentage', 'Turnover Percentage', 
                'Offensive Rebound Percentage', 'Free Throws Per Field Goal Attempt', 
                'Effective Field Goal Percentage Allowed', 'Opponent Turnover Percentage', 
                'Defensive Rebound Pecentage', 'Opponent Free Throws Per Field Goal Attempt', 'Attendance', 
                'Attendance Per Game']

def scatter_data(season):
    html = requests.get(f'http://www.basketball-reference.com/leagues/NBA_{int(season) + 1}.html').content
    time.sleep(3)
    cleaned_soup = BeautifulSoup(re.sub(rb"<!--|-->",rb"", html), features='lxml')
    misc_table = cleaned_soup.find('table', {'id':'misc_stats'})

    df = pd.read_html(str(misc_table))[0]
    df.columns = df.columns.get_level_values(1)
    df['Team'] = df['Team'].apply(lambda x: x if x[-1] != '*' else x[:-1])

    df = df.drop(['Rk', 'Arena'], axis=1).copy()

    df.columns = scatter_vals
    
    df = df[df['Team'] != 'League Average']
    df[['Wins', 'Losses']] = df[['Wins', 'Losses']].astype(int)

    return df


#%%

# %%
