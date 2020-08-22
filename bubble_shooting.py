#%%
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguegamelog
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chart_studio
api_key = f = open("plotly_key.txt", "r").readline()
chart_studio.tools.set_credentials_file(username='ethanfuerst', api_key=api_key)

show_all = True
#%%
log = leaguegamelog.LeagueGameLog(counter=0, direction='ASC', league_id='00', 
                player_or_team_abbreviation='T', season='2019-20', season_type_all_star='Regular Season')
df = log.get_data_frames()[0]

bubble_teams = set(df[pd.to_datetime(df['GAME_DATE']) > '2020-5-1']['TEAM_ABBREVIATION'])
df = df[df['TEAM_ABBREVIATION'].isin(bubble_teams)]
pre_bubble = df[pd.to_datetime(df['GAME_DATE']) < '2020-5-1']
pre_bubb_stats = pre_bubble.groupby('TEAM_NAME').sum().reset_index()[['TEAM_NAME', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA']]
pre_bubb_stats['FG%'] = round(round(pre_bubb_stats['FGM'] / pre_bubb_stats['FGA'],4) * 100,2)
pre_bubb_stats['3%'] = round(round(pre_bubb_stats['FG3M'] / pre_bubb_stats['FG3A'],4) * 100,2)
pre_bubb_stats['FT%'] = round(round(pre_bubb_stats['FTM'] / pre_bubb_stats['FTA'],4) * 100,2)
pre_bubb_stats = pre_bubb_stats[['TEAM_NAME', 'FG%', '3%', 'FT%']]

bubble = df[pd.to_datetime(df['GAME_DATE']) > '2020-5-1']
bubb_stats = bubble.groupby('TEAM_NAME').sum().reset_index()[['TEAM_NAME', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA']]
bubb_stats['FG%'] = round(round(bubb_stats['FGM'] / bubb_stats['FGA'],4) * 100,2)
bubb_stats['3%'] = round(round(bubb_stats['FG3M'] / bubb_stats['FG3A'],4) * 100,2)
bubb_stats['FT%'] = round(round(bubb_stats['FTM'] / bubb_stats['FTA'],4) * 100,2)
bubb_stats = bubb_stats[['TEAM_NAME', 'FG%', '3%', 'FT%']]

df = pd.merge(left=pre_bubb_stats, right=bubb_stats, how='inner', on='TEAM_NAME', suffixes=('_pre', '_dur'))
df['fg diff'] = df['FG%_dur'] - df['FG%_pre']
df['3 diff'] = df['3%_dur'] - df['3%_pre']
df['ft diff'] = df['FT%_dur'] - df['FT%_pre']
df['pts add from 3'] = df['3 diff']/100 * 3
df['pts add from 2'] = df['fg diff']/100 * 2
df['pts add from 1'] = df['ft diff']/100
df['total pts add'] = df['pts add from 3'] + df['pts add from 2'] + df['pts add from 1']
df['avg pts add'] = df['total pts add']/3

#%%
fig = make_subplots(rows=1, cols=3,
    subplot_titles=("Field Goal %", "Free Throw %", "3 point %"))

for pre, dur, string_, column, column_name in zip(['FG%_pre', 'FT%_pre', '3%_pre'], 
                    ['FG%_dur', 'FT%_dur', '3%_dur'],
                    ['the field', 'the line', '3'],
                    [1, 2, 3],
                    ['Pre-bubble FG%', 'Pre-bubble FT%', 'Pre-bubble 3 point%']):

    correlation_matrix = np.corrcoef(df[pre], df[dur])
    r = correlation_matrix[0,1]

    fig.add_trace(
        go.Scatter(x=df[pre], y=df[dur], mode='markers',
            hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' shot %{x}%<br>from ' + string_ + ' before the bubble<br>' +
            'and %{y}% during the bubble<extra></extra>'),
        row=1, col=column
    )

    fig.update_xaxes(title_text=column_name + '<br>r = {0}'.format(round(r, 3)), row=1, col=column)

fig.update_layout(
    height=335, 
    width=700, 
    showlegend=False, 
    title=dict(
        text="Correlation of shooting statistics before and during the bubble<br>(regular season only)",
        y=.9,
        x=.5
    )
    )

fig.update_yaxes(title_text="Bubble shooting %", row=1, col=1)

if show_all:
    fig.show()

chart_studio.plotly.plot(fig, filename='NBA bubble shooting correlation', auto_open=False)

# %%
# - fg percentage
fig = go.Figure()

for i in ['fg diff', 'FG%_pre', 'FG%_dur']:
    df = df.sort_values(i, ascending=False)
    fig.add_trace(go.Scatter(
        x=df['FG%_pre'],
        y=df['TEAM_NAME'],
        marker=dict(color="orange", size=12),
        mode="markers",
        name="Pre-bubble",
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' shot %{x}%<br>from 2 before the bubble<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df['FG%_dur'],
        y=df['TEAM_NAME'],
        marker=dict(color="blue", size=12),
        mode="markers",
        name="Bubble",
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' shot %{x}%<br>from 2 in the bubble<extra></extra>'
    ))

fig.update_layout(
        title=dict(
        text="Pre-bubble field goal shooting vs. bubble shooting<br>(regular season only)",
        y=.925,
        x=.5),
        xaxis_title="FG% (use buttons on the side to sort)",
        yaxis_title="Team",
        width=600,
        height=700,
        updatemenus=[
            dict(
            type = "buttons",
            buttons=list([
                dict(
                    args=[dict(visible=[True, True, False, False, False, False])
                            ],
                    label="Difference",
                    method="update"
                ),
                dict(
                    args=[dict(visible=[False, False, True, True, False, False])
                            ],
                    label="Pre-bubble",
                    method="update"
                ),
                dict(
                    args = [dict(visible=[False, False, False, False, True, True])
                            ],
                    label="Bubble",
                    method="update"
                )
            ]),
            direction='up',
            showactive=False,
            x=1.05,
            y=.5,
            xanchor="left",
            yanchor="bottom"
        ),
    ]
)

if show_all:
    fig.show()

chart_studio.plotly.plot(fig, filename='NBA bubble FG% difference', auto_open=False)
# %%
# - 3 percentage
fig = go.Figure()

for i in ['3 diff', '3%_pre', '3%_dur']:
    df = df.sort_values(i, ascending=False)
    fig.add_trace(go.Scatter(
        x=df['3%_pre'],
        y=df['TEAM_NAME'],
        marker=dict(color="orange", size=12),
        mode="markers",
        name="Pre-bubble",
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' shot %{x}%<br>from 3 before the bubble<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df['3%_dur'],
        y=df['TEAM_NAME'],
        marker=dict(color="blue", size=12),
        mode="markers",
        name="Bubble",
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' shot %{x}%<br>from 3 in the bubble<extra></extra>'
    ))

fig.update_layout(
        title=dict(
        text="Pre-bubble 3 point shooting vs. bubble shooting<br>(regular season only)",
        y=.925,
        x=.5),
        xaxis_title="3 point% (use buttons on the side to sort)",
        yaxis_title="Team",
        width=600,
        height=700,
        updatemenus=[
            dict(
            type = "buttons",
            buttons=list([
                dict(
                    args=[dict(visible=[True, True, False, False, False, False])
                            ],
                    label="Difference",
                    method="update"
                ),
                dict(
                    args=[dict(visible=[False, False, True, True, False, False])
                            ],
                    label="Pre-bubble",
                    method="update"
                ),
                dict(
                    args = [dict(visible=[False, False, False, False, True, True])
                            ],
                    label="Bubble",
                    method="update"
                )
            ]),
            direction='up',
            showactive=False,
            x=1.05,
            y=.5,
            xanchor="left",
            yanchor="bottom"
        ),
    ]
)

if show_all:
    fig.show()

chart_studio.plotly.plot(fig, filename='NBA bubble 3 point% difference', auto_open=False)
#%%
# - ft percentage
fig = go.Figure()

for i in ['ft diff', 'FT%_pre', 'FT%_dur']:
    df = df.sort_values(i, ascending=False)
    fig.add_trace(go.Scatter(
        x=df['FT%_pre'],
        y=df['TEAM_NAME'],
        marker=dict(color="orange", size=12),
        mode="markers",
        name="Pre-bubble",
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' shot %{x}%<br>from the line before the bubble<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df['FT%_dur'],
        y=df['TEAM_NAME'],
        marker=dict(color="blue", size=12),
        mode="markers",
        name="Bubble",
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' shot %{x}%<br>from the line in the bubble<extra></extra>'
    ))

fig.update_layout(
        title=dict(
        text="Pre-bubble free throw shooting vs. bubble shooting<br>(regular season only)",
        y=.925,
        x=.5),
        xaxis_title="FT% (use buttons on the side to sort)",
        yaxis_title="Team",
        width=600,
        height=700,
        updatemenus=[
            dict(
            type = "buttons",
            buttons=list([
                dict(
                    args=[dict(visible=[True, True, False, False, False, False])
                            ],
                    label="Difference",
                    method="update"
                ),
                dict(
                    args=[dict(visible=[False, False, True, True, False, False])
                            ],
                    label="Pre-bubble",
                    method="update"
                ),
                dict(
                    args = [dict(visible=[False, False, False, False, True, True])
                            ],
                    label="Bubble",
                    method="update"
                )
            ]),
            direction='up',
            showactive=False,
            x=1.05,
            y=.5,
            xanchor="left",
            yanchor="bottom"
        ),
    ]
)

if show_all:
    fig.show()

chart_studio.plotly.plot(fig, filename='NBA bubble FT% difference', auto_open=False)
# %%
df = df.sort_values('total pts add', ascending=False)

fig = go.Figure(data=[
    go.Bar(name='Free Throws', x=df['TEAM_NAME'], y=df['pts add from 1'],
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' added %{y}<br>points per free throw on average in the bubble<extra></extra>'),
    go.Bar(name='Field Goals', x=df['TEAM_NAME'], y=df['pts add from 2'],
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' added %{y}<br>points per field goal on average in the bubble<extra></extra>'),
    go.Bar(name='3 Pointers', x=df['TEAM_NAME'], y=df['pts add from 3'],
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' added %{y}<br>points per 3 pointer on average in the bubble<extra></extra>'),
    go.Bar(name='Total', x=df['TEAM_NAME'], y=df['total pts add'],
        hovertemplate='The '+ df['TEAM_NAME'].astype(str) +' increased their average shooting<br>in the bubble by %{y} points total<extra></extra>')
])

fig.update_layout(
    title=dict(
        text="Average points per shot difference in the bubble<br>(regular season only)",
        y=.9,
        x=.5),
    barmode='group',
    width=650,
    height=500)

if show_all:
    fig.show()

chart_studio.plotly.plot(fig, filename='NBA bubble avg pps diff', auto_open=False)

# %%

fig = go.Figure(data=[
    go.Bar(name='Free Throws', x=['Bubble teams'], y=[round(df['pts add from 1'].sum(), 3)],
        hovertemplate='Bubble teams increased their free throw<br>shooting by %{y} points per shot<br>compared to outside the bubble<extra></extra>'),
    go.Bar(name='Field Goals', x=['Bubble teams'], y=[round(df['pts add from 2'].sum(), 3)],
        hovertemplate='Bubble teams increased their field goal<br>shooting by %{y} points per shot<br>compared to outside the bubble<extra></extra>'),
    go.Bar(name='3 Pointers', x=['Bubble teams'], y=[round(df['pts add from 3'].sum(), 3)],
        hovertemplate='Bubble teams increased their 3 point<br>shooting by %{y} points per shot on average<br>compared to outside the bubble<extra></extra>'),
    go.Bar(name='Total', x=['Bubble teams'], y=[round(df['total pts add'].sum(), 3)],
        hovertemplate='Bubble teams increased their overall<br>shooting by %{y} points per shot on average<br>compared to outside the bubble<extra></extra>')
])

fig.update_layout(
    title=dict(
        text="Total average points per shot difference in the bubble<br>(regular season only)",
        y=.9,
        x=.5),
    barmode='group',
    width=650,
    height=400)

if show_all:
    fig.show()

chart_studio.plotly.plot(fig, filename='NBA bubble total pps diff', auto_open=False)

#%%
