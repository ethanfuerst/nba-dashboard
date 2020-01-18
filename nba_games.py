import pandas as pd
import numpy as np
import datetime
import html5lib
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playergamelog

# Custom errors
class PlayerNotFoundError(Exception):
    pass

class SeasonNotFoundError(Exception):
    pass

def get_player_season(player_name, season=datetime.datetime.today().year - 1, season_type='Regular Season'):
    '''
    Returns a df of player game logs from the 'season to season+1' season.
    Specify 'Regular Season', 'Pre Season', 'Playoffs' or 'All Star'.

    Parameters:

    player_name (string, required)
        The name of the player. If name is too general, then first name in the search will be returned.
            Ex. 'luka doncic' or 'harden'
        If the search does not return a player, a PlayerNotFoundError will be thrown.

    
    season (int, default: current year - 1)
        The season that you want to pull data from. 
            Ex. 2003
        If the player you specified doesn't have date from the season inputted, a SeasonNotFoundError will be thrown.
        
    season_type (string, default: 'Regular Season')
        The period of games from which you'd like the data from.
        Must be one of the following:
            'Regular Season'
            'Pre Season'
            'Playoffs'
            'All-Star'
            'All Star'
        If season_type is not one of the values above, it will be changed to 'Regular Season'.

    Returns:

    df
        A pd.DataFrame() containing the player data with the following columns:
            ['SEASON_ID', 'Player_ID', 'Game_ID', 'GAME_DATE', 'MATCHUP', 'WL',
            'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM',
            'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 
            'PF', 'PTS', 'PLUS_MINUS']
    '''
    
    # Change season_type to 'Regular Season' if not specified correctly
    if season_type not in ['Regular Season', 'Pre Season', 'Playoffs', 'All-Star', 'All Star']:
        season_type = 'Regular Season'

    # Search for the player to get the id
    player_search = players.find_players_by_full_name(player_name)

    # If no results for the player, throw an error
    if len(player_search) == 0:
        raise PlayerNotFoundError('Name not found in database. Try being more specific or look for the player here: https://stats.nba.com/players/')

    # Get the id from the result of my search
    player_id = player_search[0]['id']

    # playergamelog is a nba_api class that contains the dataframes
    log = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star=season_type)

    # If no results for the season, throw an error
    if len(log.get_data_frames()[0]) == 0:
        raise SeasonNotFoundError("'" + player_name + "'" + " doesn't have data recorded for the " +  str(season) + " season." )

    df = log.get_data_frames()[0]
    
    # Drop the 'video available' column
    df.drop(['VIDEO_AVAILABLE'], axis=1, inplace=True)
    return df

def get_season(season=datetime.datetime.today().year - 1, season_type='Regular Season'):
    '''
    Returns a df of NBA season data in the 'season to season+1' season.

    Parameters:

    season (int, default: current year - 1)
        The season that you want to pull data from. 
            Ex. 2008
        If the season you inputted isn't an integer, a TypeError will be thrown.
    
    season_type (string, default: 'Regular Season')
        The period of games from which you'd like the data from.
            Must be either 'Regular Season' or 'Playoffs'.
        If season_type is not one of the values above, it will be changed to 'Regular Season'.


    Returns:

    df
        A pd.DataFrame() containing the season data with the following columns:
            ['Date', 'Start (ET)', 'Visitor/Neutral', PTS', 'Home/Neutral',
            'PTS.1', 'OT', 'Attend.', 'Season', 'Year','MOV']
    '''

    # Change season_type to 'Regular Season' if not specified correctly
    if season_type not in ['Regular Season', 'Playoffs']:
        season_type = 'Regular Season'
    
    # Add one to season, that's the logic on basketball-reference.com
    try:
        season = int(season)
        season = season + 1
    except:
        # This is probably because they inputted a string for season, and we need an int
        raise TypeError("Wrong variable type for season. Integer expected.")

    # The season goes from October to June usually, so we will go from July to June to capture all data
    months = [datetime.date(2019, i, 1).strftime('%B').lower() for i in list(range(7, 13)) + list(range(1,7))]

    # Getting the list of URLs with our months list
    urls = []
    for i in months:
        urls.append('https://www.basketball-reference.com/leagues/NBA_' + str(season) + '_games-' + str(i) + '.html')
    
    games = pd.DataFrame()
    for url in urls:
        try:
            month = pd.read_html(url)[0]
            month.drop(['Notes','Unnamed: 6'], axis=1, inplace=True)
            month.dropna(subset=['PTS'], inplace=True)
            games = pd.concat([games, month], sort=False)
        except:
            pass
    
    # This method will clean the games dataframe before it is returned
    def clean_games(df):
        season = "'" +str(int(url.split('_')[1]) - 1)[2:] + " - '" + str(url.split('_')[1])[2:]
        df['Season'] = season
        df['Year'] = pd.to_datetime(df['Date']).dt.year
        df['PTS'] = df['PTS'].astype(int)
        df['PTS.1'] = df['PTS.1'].astype(int)
        df['MOV'] = abs(df['PTS'] - df['PTS.1'])
        df['Date'] = pd.to_datetime(df['Date'])
        df['Start (ET)'] = pd.to_datetime(df['Start (ET)'])
        df['OT'] = df['OT'].fillna('No overtime')
        return df
    
    # Reset the index and rename the overtime column
    games.reset_index(inplace=True, drop=True)
    games.rename(columns={'Unnamed: 7': 'OT'}, inplace=True)

    try:
        playoff_start = games[games['Date'] == 'Playoffs'].index[0]
    except:
        # The specified season doeesn't contain playoff games
        return clean_games(games)

    if season_type == 'Regular Season':
        # Return all games before the playoff_start
        return clean_games(games[games.index < playoff_start].copy())
    else:
        # Return all games after the playoff_start 
        return clean_games(games[games.index > playoff_start].copy())

def thres_games(startyear=2000, endyear=datetime.datetime.today().year - 1, thres = 40):
    '''
    Returns a df detailing the number of games won by a number >= the threshold specified.

    Parameters:


    startyear (int, default: 2001)
        The first season that you want to be in the df.
            ex. 2015

    endyear (int, default: current year - 1)
        The last season that you want to be in the df.
            ex. 2019
    
    thres (int, default: 40)
        The margin of victory threshold for the df.
            ex. 30
    

    Returns:

    df
        A pd.DataFrame() containing the season data with the following columns:
            ['Season', 'Count', 'Game Nums', 'Projected']
            'Count' is the number of games over thres.
            'Projected' is for current seasons in play only.
    '''

    # Need to make sure that startyear, endyear and thres are all integers
    try:
        startyear = int(startyear)
        endyear = int(endyear)
        thres = int(thres)
    except:
        # This is probably because they inputted a string for season, and we need an int
        raise TypeError("Wrong variable type for startyear, endyear or thres. Integer expected.")
    # Need to check that endyear season exists
    try:
        # If there is data for endyear, we are good.
        get_season(endyear)
    except:
        # If we can't get data from endyear, then raise SeasonNotFoundError
        raise SeasonNotFoundError("There is no data for the " + str(endyear) + " season yet.")

    years = [i for i in range(startyear, endyear + 1)]
    tot = []
    for i in years:
        year = get_season(i)
        num_games = len(year)
        season = "'" +str(i)[2:] + " - '" + str(i + 1)[2:]
        game_nums = list(year[year['MOV'] >= thres].index + 1)
        year = year[year['MOV'] >= thres].copy()
        count = len(year)
        Projected = int(((count / num_games) * 1230) - count)
        tot.append([season, count, game_nums, Projected])
    
    return pd.DataFrame(tot, columns=['Season', 'Count', 'Game Nums', 'Projected'])
