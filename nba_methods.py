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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
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

def zone_label(row):
    '''
    Creates zone for shots
    '''
    if row['SHOT_ZONE_RANGE'] == '8-16 ft.':
        if row['SHOT_ZONE_AREA'] == 'Left Side(L)':
            return '8-16 ft. (L)'
        elif row['SHOT_ZONE_AREA'] == 'Right Side(L)':
            return '8-16 ft. (R)'
        else:
            return '8-16 ft. (C)'
    if row['SHOT_ZONE_RANGE'] == '16-24 ft.':
        if row['SHOT_ZONE_AREA'] == 'Left Side(L)':
            return '16-24 ft. (L)'
        elif row['SHOT_ZONE_AREA'] == 'Right Side(L)':
            return '16-24 ft. (R)'
        elif row['SHOT_ZONE_AREA'] == 'Left Side Center(LC)':
            return '16-24 ft. (LC)'
        elif row['SHOT_ZONE_AREA'] == 'Right Side Center(LC)':
            return '16-24 ft. (RC)'
        else:
            return 'Mid Range (C)'
    elif row['SHOT_ZONE_BASIC'] == 'Left Corner 3':
        return 'Left Corner 3'
    elif row['SHOT_ZONE_BASIC'] == 'Right Corner 3':
        return 'Right Corner 3'
    elif row['SHOT_ZONE_BASIC'] == 'Above the Break 3':
        # 3's
        if row['SHOT_ZONE_AREA'] == 'Left Side Center(LC)':
            return '3 Pointer (LC)'
        elif row['SHOT_ZONE_AREA'] == 'Right Side Center(LC)':
            return '3 Pointer (RC)'
        elif row['SHOT_ZONE_AREA'] == 'Center(C)':
            return '3 Pointer (C)'
        else:
            return 'Backcourt'
    elif row['SHOT_ZONE_RANGE'] == 'Less Than 8 ft.':
        return 'Less Than 8 ft.'
    else:
        return 'Backcourt'

def shots_grouper(shots, avgs):
    '''
    returns df ready for make_shot_chart from shots, avgs dfs
    '''
    # Change zones
    shots['ZONE'] = shots.apply(lambda row: zone_label(row), axis=1)
    avgs['ZONE'] = avgs.apply(lambda row: zone_label(row), axis=1)

    shots_group = shots.groupby(by=['ZONE']).sum().reset_index()[['ZONE', 'SHOT_ATTEMPTED_FLAG', 'SHOT_MADE_FLAG']].copy()
    shots_group['AVG_FG_PCT'] = round(shots_group['SHOT_MADE_FLAG'] / shots_group['SHOT_ATTEMPTED_FLAG'], 3)

    avgs = avgs.groupby(by=['ZONE']).sum().reset_index()
    avgs['AVG_FG_PCT'] = round(avgs['FGM'] / avgs['FGA'], 3)
    avgs = avgs.drop('FG_PCT', axis=1)

    merged = pd.merge(shots_group, avgs, on=['ZONE']).copy()
    merged = merged.rename({'AVG_FG_PCT_x': 'PLAYER_PCT', 'AVG_FG_PCT_y':'LEAGUE_PCT'}, axis=1).copy()
    merged['PCT_DIFF'] = merged['PLAYER_PCT'] - merged['LEAGUE_PCT']

    to_plot = pd.merge(shots, merged, on=['ZONE'])[['LOC_X', 'LOC_Y', 'SHOT_ATTEMPTED_FLAG_x',	'SHOT_MADE_FLAG_x', 'ZONE', 'PCT_DIFF']]

    return to_plot


def make_shot_chart(df, kind='normal', title=None, title_size=14, context=None, context_size=12, 
                        show_misses=True, make_marker='o', miss_marker= 'x', make_marker_size=18, miss_marker_size=20, make_marker_color='#007A33', miss_marker_color='#C80A18',
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
        show_misses (boolean, default: True)
        
        make_marker (string, default: 'o')
            Marker for the made shots

        miss_marker (string, default: 'x')
            Marker for missed shots

        make_marker_size (integer, default: 18)
            Marker size for made shots

        miss_marker_size (integer, default: 20)
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
    
    df['PCT_DIFF_scaled'] = df['PCT_DIFF']

    if kind == 'normal':
        df_1 = df[df['SHOT_MADE_FLAG_x'] == 1].copy()
        plt.scatter(df_1['LOC_X'], df_1['LOC_Y'], s=make_marker_size, marker=make_marker, c=make_marker_color)
        if show_misses:
            df_2 = df[df['SHOT_MADE_FLAG_x'] == 0].copy()
            plt.scatter(df_2['LOC_X'], df_2['LOC_Y'], s=miss_marker_size, marker=miss_marker, c=miss_marker_color)
    elif kind == 'hex':
        hexbins = ax.hexbin(df['LOC_X'], df['LOC_Y'], gridsize=hex_grid, 
                    extent=[-275, 275, -50, 425], cmap=cm.get_cmap('RdYlBu_r'))
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

    if kind == 'hex':
        axins1 = inset_axes(ax, width="15%", height="2%", loc='lower left')
        cbar = fig.colorbar(hexbins, cax=axins1, orientation="horizontal", ticks=[-1, 1])
        interval = hexbins.get_clim()[1] - hexbins.get_clim()[0]
        ltick = hexbins.get_clim()[0] + (interval * .2)
        rtick = hexbins.get_clim()[1] - (interval * .2)
        cbar.set_ticks([ltick, rtick])
        cbar.set_ticklabels(['Below', 'Above'])
        axins1.xaxis.set_ticks_position('top')
        cbar.ax.set_title('Compared to \nLeague Average', fontsize=10)

        # Sizes are wrong
        offsets = hexbins.get_offsets()
        orgpath = hexbins.get_paths()[0]
        verts = orgpath.vertices
        values = hexbins.get_array()
        ma = values.max()
        patches = []
        for offset,val in zip(offsets,values):
            v1 = verts*val/ma+offset
            path = Path(v1, orgpath.codes)
            patch = PathPatch(path)
            patches.append(patch)

        pc = PatchCollection(patches, cmap=cm.get_cmap('RdYlBu_r'), edgecolors='black')
        pc.set_array(values)
        ax.add_collection(pc)
        hexbins.remove()

    return plt