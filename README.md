# nba_vis

This project is where I keep all my files that I use when I analyze all sorts of NBA data.

## Files in this repository

__*margin_of_victory.py*__ - .py file with analysis that showed the '19 - '20 season is set to have the most 40-point blowouts of all time. [Here is my completed analysis.](https://www.reddit.com/r/nba/comments/eg2own/oc_this_season_is_on_pace_for_a_record_number_of/)

__*player_games.py*__ - .py file to pull a players game log for a season

__*nba_games.py*__ - .py file with methods to help pull data from [basketball-reference.com](https://www.basketball-reference.com), [NPA API](https://github.com/swar/nba_api/), and other sources.

__*.gitignore*__ - shows github what files to ignore when I commit my changes.

## TODO

- [x] create get_player_season() and put in nba_games
- [x] make sure get_year() works for all years
  - [x] clean up the logic behind what get_year() returns
- [ ] why are there so many blowouts this year? - create new .py file and dig in to it
- [ ] dig in to ppfta, ppfga, pp3pa on player_games.py
- [ ] create class with all player/team data
