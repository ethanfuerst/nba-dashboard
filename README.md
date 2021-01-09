# nba_vis

This project is where I keep all my files that I use when I analyze all sorts of NBA data.

## Files in this repository

### /projects/

#### a few ad-hoc analyses

__*2020_mvp.ipynb*__ - detailed analysis of the 2020 NBA MVP race between LeBron and Giannis (as of 5/30/20) [Here is my completed analysis.](https://tidbitstatistics.com/nba-mvp/)

__*bubble_playoff_h-a.ipynb*__ -  compared home/away records over the last 15 years. [Here is my completed analysis.](https://www.tidbitstatistics.com/are-nba-teams-shooting-better-in-the-bubble/)

__*bubble_shooting.ipynb*__ - comparing shooting number before and during the 2019-20 NBA bubble. [Here is my completed analysis.](https://www.tidbitstatistics.com/are-nba-teams-shooting-better-in-the-bubble/)

__*margin_of_victory.ipynb*__ - showed the '19 - '20 season was on pace to have the most 40-point blowouts of all time. (as of 12/26/19) [Here is my completed analysis.](https://www.tidbitstatistics.com/NBA-blowouts/)

### /nba_dashboard/

#### code for my NBA Season dashboard

__*app.<span></span>py*__ - the meat of my application. [Here is the completed dashboard.](https://tidbitstatistics.com/nba-season-dashboard/)

__*nba_data.py*__ - the bones of my application, gathers all data from various sources and formats for usage in app.<span></span>py

__*Procfile, requirements.txt*__ - other files needed for app<span></span>.py to run

### everything else

__*nba_player.py*__ - contains NBA_Player() object

__*nba_team.py*__ - contains NBA_Team() object

__*nba_season.py*__ - contains NBA_Season() object

__*nba_methods.py*__ - contains various methods to support NBA-related objects I have built in other files

__*push_heroku_changes.sh*__ - shell script to updated dashboard changes in heroku

## TODO

- [ ] why are there so many blowouts this year? - create new .py file and dig in to it
- [x] add get_shot_chart() method to NBA_Player class
  - [x] pull data frames
  - [ ] create shot chart from data frames
    - [x] figure out fix, ax
    - [x] colors and background color
    - [x] limiters for the shots
    - [x] kwargs handling
    - [x] team_id df in \_\_init__ method
    - [x] add abbreviation functionality for get_shot_chart
    - [x] chart design
      - [x] add colorbar for hexbins
      - [x] hardwood floor? or other texture?
      - [x] legend as color scale
        - [x] move color ticks to percentile of cbar
    - [x] determine zones
    - [x] hex size as frequency
      - [x] fix hex size plot error
    - [x] fix team/date error (can pass in 0 for teamid)
    - [x] fix scale error in nba_methods
    - [x] add 2pt% and 3pt% on chart
      - [x] if hex kind then add above the legends
    - [x] fix error for make_shot_chart
    - [x] fix playoff data from nba_team.py
    - [ ] parameter for size on/off in hexbins
    - [ ] team logo on chart?
- [ ] create Plotly Dash dashboard to analyze a season's worth of data
  - [ ] find a way to format the dashboard and make it look good
- [ ] add get_shot_dist() method to NBA_Player class
  - [x] histogram with shot dist and freq
  - [ ] brainstorm kinds of charts and figure out parameter control
    - [ ] add bar color - one val or the different shooting %ages
    - [ ] stacked histogram for makes and misses
- [ ] make method when given x players it will compare stats similar to MVP analysis blog post
