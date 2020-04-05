import pandas as pd
pd.options.display.max_columns = None
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Circle, Rectangle, Arc
import datetime
import html5lib
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, playercareerstats, shotchartdetail, shotchartlineupdetail
from nba_season import NBA_Season
from nba_methods import make_shot_chart

# Custom errors
class PlayerNotFoundError(Exception):
    pass

class SeasonNotFoundError(Exception):
    pass


class NBA_Team():
    def __init__(self, team_name):
        return