import pandas as pd
import numpy as np
import datetime
import html5lib

def get_year(year, playoffs=False):
    '''
    Returns a df of NBA season data when given a year. 'year-1 to year' season.
    Specify if playoffs are wanted too with playoffs variable (boolean).
    '''
    months = [datetime.date(2019, i, 1).strftime('%B').lower() for i in list(range(7, 13)) + list(range(1,7))]

    urls = []
    for i in months:
        urls.append('https://www.basketball-reference.com/leagues/NBA_' + str(year) + '_games-' + str(i) + '.html')
    
    games = pd.DataFrame()
    for url in urls:
        try:
            month = pd.read_html(url)[0]
            month.drop(['Notes','Unnamed: 6'], axis=1, inplace=True)
            month.dropna(subset=['PTS'], inplace=True)
            games = pd.concat([games, month], sort=False)
        except:
            pass
    
    def clean_games(df):
        season = "'" +str(int(url.split('_')[1]) - 1)[2:] + " - '" + str(url.split('_')[1])[2:]
        df['season'] = season
        df['year'] = pd.to_datetime(df['Date']).dt.year
        df['PTS'] = df['PTS'].astype(int)
        df['PTS.1'] = df['PTS.1'].astype(int)
        df['mov'] = abs(df['PTS'] - df['PTS.1'])
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    games.reset_index(inplace=True, drop=True)
    games.rename(columns={'Unnamed: 7': 'OT'}, inplace=True)

    # Logic breaks down here for seasons with less than 1230 games
    # But for the most part this works
    if len(games[games['Date'] == 'Playoffs']) == 0:
        return clean_games(games)
    playoff_start = games[games['Date'] == 'Playoffs'].index[0]
    games = clean_games(games[games.index < playoff_start].copy())
    if len(games) < 1230 and playoff_start < 1230:
        if playoffs:
            playoff_games = clean_games(games[games.index > playoff_start].copy())
            return games, playoff_games
        else:
            return games
    elif not playoffs:
        games = clean_games(games[games.index < playoff_start].copy())
        return games
    else:
        playoff_games = clean_games(games[games.index > playoff_start].copy())
        games = clean_games(games[games.index < playoff_start].copy())
        return games, playoff_games

def thres_games(startyear=2001, endyear=2021, thres = 40):
    '''
    Returns a df with the following columns when given a startyear, endyear and a thres.
    Thres is the margin of victory thresold.
    Columns: 'Season', 'Count' (of games over thres),  
            'Projected' (for seasons in play only), 'Games before All-star'
    '''
    years = [i for i in range(startyear, endyear)]
    tot = []
    star = pd.read_html('https://www.basketball-reference.com/allstar/')[1]
    for i in years:
        year = get_year(i)
        num_games = len(year)
        season = "'" +str(i - 1)[2:] + " - '" + str(i)[2:]
        game_nums = list(year[year['mov'] >= thres].index + 1)
        # print(i)
        a_star = ''
        if len(star[star['Year'] == year]) == 0:
            a_star = 'None'
        else:
            a_star = len(year[year['Date'] < pd.to_datetime(star[star['Year'] == i]['Date'].iloc[0])])
        year = year[year['mov'] >= thres].copy()
        count = len(year)
        Projected = int(((count / num_games) * 1230) - count)
        tot.append([season, count, game_nums, Projected, a_star])
    
    return pd.DataFrame(tot, columns=['Season', 'Count', 'Game Nums', 'Projected', 'Games before All-star'])
