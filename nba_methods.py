import pandas as pd
pd.options.display.max_columns = None
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Circle, Rectangle, Arc, PathPatch
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
import datetime
import html5lib
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, playercareerstats, shotchartdetail, shotchartlineupdetail
from nba_season import NBA_Season


# Custom errors
class PlayerNotFoundError(Exception):
    pass

class SeasonNotFoundError(Exception):
    pass


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

def draw_court(color='black', lw=2):
    '''
    From http://savvastjortjoglou.com/nba-shot-sharts.html
    '''
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='dashed')
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)
    outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False)

    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                        bottom_free_throw, restricted, corner_three_a,
                        corner_three_b, three_arc, center_outer_arc,
                        center_inner_arc, outer_lines]

    return court_elements


def make_shot_chart(df, kind='normal', title=None, title_size=14, context=None, context_size=12, 
                        show_misses=False, make_marker='o', miss_marker= 'o', make_marker_size=11, miss_marker_size=11, make_marker_color='#007A33', miss_marker_color='#C80A18',
                        hex_grid=50):
        '''
        Returns a matplotlib fig of the player's shot chart given certain parameters.

        Parameters:
        
        kind (string, default: 'normal')
            'normal' or 'hex'
            Kind of shot chart
            'normal' - shows makes as dots
                Best for single game
            'hex' - shows frequency of shots in area as size of hex and color of zone compared to league average in zone
                Best for multiple games or players
        
        title (string, default: None)
            The title on the top of the figure

        title_size (integer, default: 14)
            The title on the top of the figure
        
        context (string, default: None)
            Text on the bottom of the plot.
            Used to add context about a plot.
        
        context_size (integer, default: 12)
            context fontsize

        'normal' parameters:
            show_misses (boolean, default: False)
                Only for kind = 'normal'
            
            make_marker (string, default: 'o')
                Marker for the made shots

            miss_marker (string, default: 'o')
                Marker for missed shots

            make_marker_size (integer, default: 11)
                Marker size for made shots

            miss_marker_size (integer, default: 11)
                Marker size for missed shots

            make_marker_color (string, default: '#007A33' - green)
                Marker color for made shots

            miss_marker_color (string, default: '#C80A18' - red)
                Marker color for missed shots

        'hex' parameters:
            hex_grid (integer, default: 50)
                Number of hexes in the axis of each grid
                Larger number = smaller hexes

        Returns:

        plt
            plt of shot data
        '''
        # This method will create the shot chart given a df created from the get_shot_chart method
        background_color = '#d9d9d9'
        fig, ax = plt.subplots(facecolor=background_color, figsize=(10,10))
        fig.patch.set_facecolor(background_color)
        ax.patch.set_facecolor(background_color)

        if title is not None:
            plt.title(title, fontdict={'fontsize': title_size})
        
        df_1 = df[df['SHOT_MADE_FLAG_x'] == 1].copy()
        if kind == 'normal':
            plt.scatter(df_1['LOC_X'], df_1['LOC_Y'], s=make_marker_size, marker=make_marker, c=make_marker_color)
            if show_misses:
                df_2 = df[df['SHOT_MADE_FLAG_x'] == 0].copy()
                plt.scatter(df_2['LOC_X'], df_2['LOC_Y'], s=miss_marker_size, marker=miss_marker, c=miss_marker_color)
        elif kind == 'hex':
            df_1['PCT_DIFF_scaled'] = df_1['PCT_DIFF'] + .5
            ax.hexbin(df_1['LOC_X'], df_1['LOC_Y'],C=df_1['PCT_DIFF_scaled'], bins=20, gridsize=hex_grid, extent=[-275, 275, -50, 425])

            plt.legend(handles=[mpatches.Patch(color='#A70022', label='Above league average'),
                    mpatches.Patch(color='#303297', label='Below league average')], 
                    facecolor='#d9d9d9', loc='lower left', edgecolor='black', framealpha=1)
            plt.text(196, 414, 'The larger hexagons\nrepresent a higher\ndensity of shots',
                        horizontalalignment='center', bbox=dict(facecolor='#d9d9d9', boxstyle='round'))

        else:
            # Might make another kind of shot chart later
            pass
        
        court_elements = draw_court()
        for element in court_elements:
            ax.add_patch(element)
        
        img = plt.imread("basketball-floor-texture.png")
        plt.imshow(img,zorder=0, extent=[-275, 275, -50, 425])
        
        if context is not None:
            ax.text(0, 435, s=context, fontsize=context_size, ha='center')

        plt.xlim(-250,250)
        plt.ylim(422.5, -47.5)
        plt.axis(False)
        return plt