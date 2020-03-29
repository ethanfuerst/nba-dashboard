import pandas as pd
import numpy as np
import datetime
import html5lib
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, playercareerstats, shotchartdetail

# Custom errors
class PlayerNotFoundError(Exception):
    pass

class SeasonNotFoundError(Exception):
    pass

class NBA_Player:
    def __init__(self, player_name):
        '''
        Player object from nba_api

        Parameters:

        player_name (string, required)
        The name of the player. If name is too general, then first name in the search will be returned.
            Ex. 'luka doncic' or 'harden'
        If the search does not return a player, a PlayerNotFoundError will be thrown.
        '''

        # Search for the player to get the id
        player_search = players.find_players_by_full_name(player_name)

        # If no results for the player, throw an error
        if len(player_search) == 0:
            raise PlayerNotFoundError('Name not found in database. Try being more specific or look for the player here: https://stats.nba.com/players/')

        # Get the id from the result of my search
        self.player_id = player_search[0]['id']
        self.name = player_search[0]['full_name']
        self.first_name = player_search[0]['first_name']
        self.last_name = player_search[0]['last_name']
        self.is_active = player_search[0]['is_active']
        # Create a df that outlines the players career
        df = self.get_career()
        df = df[df['Team'] != 'TOT'][['Season', 'Team', 'TEAM_ID']].copy()
        df['start'] = df['Season'].apply(lambda x: int(x[:4]))
        df['end'] = df['start'] + 1
        self.career = df
    
    def get_season(self, season=datetime.datetime.today().year - 1, season_type='regular'):
        '''
        Returns a df of player game logs from the 'season to season+1' season.
        Specify 'regular', 'preseason', 'playoffs' or 'allstar'.

        Parameters:

        season (int, default: current year - 1)
            The season that you want to pull data from. 
                Ex. 2003
            If the player you specified doesn't have date from the season inputted, a SeasonNotFoundError will be thrown.
            
        season_type (string, default: 'regular')
            The period of games from which you'd like the data from.
            Must be one of the following:
                'regular' - Regular Season
                'preseason' - Pre-Season
                'playoffs' - Playoffs
                'allstar' - All-Star
            If season_type is not one of the values above, it will be changed to 'regular'.

        Returns:

        df
            A pd.DataFrame() containing the player data with the following columns:
                ['Season', 'Player', 'Game_ID', 'GAME_DATE', 'MATCHUP', 'WL',
                'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
                'FT_PCT', 'TS_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                'PTS', 'PLUS_MINUS']
        '''
        # Change season_type to 'regular' if not specified correctly
        if season_type not in ['regular', 'preseason', 'playoffs', 'allstar']:
            season_type = 'regular'
        
        s_types = {'regular':'Regular Season', 'preseason':'Pre-Season', 'playoffs':'Playoffs', 'allstar':'All-Star'}
        s_type = s_types[season_type]

        # playergamelog is a nba_api class that contains the dataframes
        try:
            log = playergamelog.PlayerGameLog(player_id=self.player_id, season=season, season_type_all_star=s_type)
        except:
            return pd.DataFrame()

        # If no results for the season, throw an error
        if len(log.get_data_frames()[0]) == 0:
            raise SeasonNotFoundError(self.name + " doesn't have data recorded for the " +  str(season) + " season." )

        df = log.get_data_frames()[0]
        df['Player'] = self.name
        df['Season'] = str(season) + "-" + str(season + 1)[2:]
        df['TS_PCT'] = round(df['PTS'] / (2*(df['FGA'] + (.44 * df['FTA']))),3)

        # Drop the 'video available' column and reorder
        df = df[['Season', 'Player', 'Game_ID', 'GAME_DATE', 'MATCHUP', 'WL',
                'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
                'FT_PCT', 'TS_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                'PTS', 'PLUS_MINUS']]
        
        return df
    
    def get_career(self):
        '''
        Returns a df of the player's totals and percentages for all season in the player's career.

        Parameters:

        season (int, default: current year - 1)
            The season that you want to pull data from. 
                Ex. 2003
            If the player you specified doesn't have date from the season inputted, a SeasonNotFoundError will be thrown.
        
        Returns:

        df
            A pd.DataFrame() containing the player data with the following columns:
                ['Player', 'Season', 'Team', 'TEAM_ID', 
                'PLAYER_AGE', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A',
                'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'TS_PCT', 'OREB', 'DREB', 'REB', 'AST', 
                'STL', 'BLK', 'TOV', 'PF', 'PTS']
        '''
        # see more on https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/playercareerstats.md
        log = playercareerstats.PlayerCareerStats(player_id=self.player_id, per_mode36='Totals')
        df = log.get_data_frames()[0]

        df['Player'] = self.name
        df['Season'] = df['SEASON_ID'].copy()
        df['Team'] = df['TEAM_ABBREVIATION'].copy()
        df['TS_PCT'] = round(df['PTS'] / (2*(df['FGA'] + (.44 * df['FTA']))),3)

        # Specify column order
        df = df[['Player', 'Season', 'Team', 'TEAM_ID', 
                'PLAYER_AGE', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A',
                'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'TS_PCT', 'OREB', 'DREB', 'REB', 'AST', 
                'STL', 'BLK', 'TOV', 'PF', 'PTS']].copy()
                
        return df

    def get_full_career(self, season_type='regular'):
        '''
        Returns a df of the player's game logs for all season in the player's career.

        Parameters:

        season_type (string, default: 'regular')
            The period of games from which you'd like the data from.
            Must be one of the following:
                'regular' - Regular Season
                'preseason' - Pre-Season
                'playoffs' - Playoffs
                'allstar' - All-Star
                'full' - Regular Season and Playoffs
                'all' - Pre-Season, Regular Season, Playoffs and All-Star
                'no_all_star' - Pre-Season, Regular Season and Playoffs
            If season_type is not one of the values above, it will be changed to 'regular'.
        
        Returns:

        df
            A pd.DataFrame() containing the player data with the following columns:
                ['Player', 'Season', 'Team', 'TEAM_ID', 
                'PLAYER_AGE', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A',
                'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'TS_PCT', 'OREB', 'DREB', 'REB', 'AST', 
                'STL', 'BLK', 'TOV', 'PF', 'PTS']
        '''
        # Get list of seasons with data
        career_seasons = self.get_career()
        seasons = [int(i[:4]) for i in career_seasons['Season'].values.astype(str)]

        # Get data from each season
        df = pd.DataFrame()
        for i in seasons:
            if season_type == 'preseason' or season_type == 'all' or season_type == 'no_all_star':
                try:
                    df_1 = self.get_season(i, season_type='preseason')
                    df_1['Season Type'] = 'PRE'
                    print(i, season_type, len(df_1), 'pre')
                    df = df.append(df_1)
                except SeasonNotFoundError:
                    pass
            if season_type == 'regular' or season_type == 'full' or season_type == 'all' or season_type == 'no_all_star':
                try:
                    df_2 = self.get_season(i, season_type='regular')
                    df_2['Season Type'] = 'REG'
                    print(i, season_type, len(df_2), 'reg')
                    df = df.append(df_2)
                except SeasonNotFoundError:
                    pass
            if season_type == 'playoffs' or season_type == 'full' or season_type == 'all' or season_type == 'no_all_star':
                # Add flag if player had no data in playoffs
                try:
                    df_3 = self.get_season(i, season_type='playoffs')
                    df_3['Season Type'] = 'PLAY'
                    print(i, season_type, len(df_3), 'playoffs')
                    df = df.append(df_3)
                except SeasonNotFoundError:
                    pass
            if season_type == 'allstar' or season_type == 'all':
                try:
                    df_4 = self.get_season(i, season_type='allstar')
                    df_4['Season Type'] = 'ALLSTAR'
                    print(i, season_type, len(df_4), 'allstar')
                    df = df.append(df_4)
                except SeasonNotFoundError:
                    pass

        df.reset_index(inplace=True)
        df = df[['Season', 'Season Type', 'Player', 'Game_ID', 'GAME_DATE', 'MATCHUP', 'WL', 
                'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
                'FT_PCT', 'TS_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV',
                'PF', 'PTS', 'PLUS_MINUS']].copy()
        cols_as_int = ['MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 
                        'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']
        df[cols_as_int] = df[cols_as_int].astype(int)

        return df
    
    def get_shot_chart(self):
        log = shotchartdetail.ShotChartDetail(team_id=1610612742, player_id=1629029)
        df = log.get_data_frames()[0]
        pass


class NBA_Season:
    def __init__(self, season=datetime.datetime.today().year - 1):
        '''
        Season object using data from basketball-reference.com

        Parameters:

        season (int, default: current year - 1)
            The season that you want to pull data from. 
                Ex. 2008
            If the season you inputted isn't an integer, a TypeError will be thrown.
        '''

        try:
            season = int(season)
        except:
            # This is probably because they inputted a string for season, and we need an int
            raise TypeError("Wrong variable type for season. Integer expected.")
        self.season = season
        self.season_str = str(season) + "-" + str(season + 1)[2:]

        # basketball-reference references the season by the second year in each season, so we need to add 1 to the season
        season = self.season + 1
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
        
        # Reset the index and rename the overtime column
        games.reset_index(inplace=True, drop=True)
        games.rename(columns={'Unnamed: 7': 'OT'}, inplace=True)

        self.games = games

        try:
            self.playoff_start = self.games[self.games['Date'] == 'playoffs'].index[0]
        except:
            # The specified season doeesn't contain playoff games
            self.playoff_start = None
    
    # Private method
    def __clean_games(self, df):
        df['Season'] = self.season_str
        df['Year'] = pd.to_datetime(df['Date']).dt.year
        df['PTS'] = df['PTS'].astype(int)
        df['PTS.1'] = df['PTS.1'].astype(int)
        df['MOV'] = abs(df['PTS'] - df['PTS.1'])
        df['Date'] = pd.to_datetime(df['Date'])
        df['Start (ET)'] = pd.to_datetime(df['Start (ET)'])
        df['OT'] = df['OT'].fillna('No overtime')
        return df
    
    def get_season(self):
        if self.playoff_start == None:
            return self.__clean_games(self.games.copy())
        else:
            return self.__clean_games(self.games[self.games.index < self.playoff_start].copy())
    
    def get_play(self):
        if self.playoff_start == None:
            raise SeasonNotFoundError("There are no play recorded for the " + self.season_str + " season.")
        else:
            return self.__clean_games(self.games[self.games.index > self.playoff_start].copy())

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
        Season(endyear)
    except:
        # If we can't get data from endyear, then raise SeasonNotFoundError
        raise SeasonNotFoundError("There is no data for the " + str(endyear) + " season yet.")

    years = [i for i in range(startyear, endyear + 1)]
    tot = []
    for i in years:
        curr_season = NBA_Season(i)
        year = curr_season.get_season()
        num_games = len(year)
        season = "'" +str(i)[2:] + " - '" + str(i + 1)[2:]
        game_nums = list(year[year['MOV'] >= thres].index + 1)
        year = year[year['MOV'] >= thres].copy()
        count = len(year)
        Projected = int(((count / num_games) * 1230) - count)
        tot.append([season, count, game_nums, Projected])
    
    return pd.DataFrame(tot, columns=['Season', 'Count', 'Game Nums', 'Projected'])
