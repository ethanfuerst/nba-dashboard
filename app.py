import sys
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash import dash_table as dt
from dash import dcc, html
from dash.dependencies import Input, Output

from figure_styles import center_style, conf_table_params, table_params
from nba_data import conf_table_cols, conf_table_data, team_colors

playoff_splitter = lambda x: [j.rsplit(" -")[0] for j in x["Team"].values]

show_playoff_markers = False

playoff_markers = (
    [
        html.H2("Conference clinched: -z"),
        html.H2("Division clinched: - y"),
        html.H2("Playoff spot clinched: - x"),
        html.H2("Missed Playoffs: - e"),
    ]
    if show_playoff_markers
    else []
)


app = dash.Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)
server = app.server
app.layout = html.Div(
    [
        dbc.Row(html.H1(children="NBA Regular Season Dashboard", style=center_style)),
        html.Div(
            [
                dcc.Dropdown(
                    id="season_val",
                    options=[
                        {"label": str(i) + "-" + str(i + 1)[2:] + " Season", "value": i}
                        for i in range(2012, 2020)
                    ],
                    value="2019",
                )
            ],
            style={
                "width": "20%",
                "padding-left": "40%",
                "padding-right": "40%",
                "textAlign": "center",
            },
        ),
        dbc.Row(
            html.H2(
                children=f'Last Updated: {datetime.now().strftime("%-I:%M:%S %p")} CST',
                style=center_style,
            )
        ),
        html.Br(),
        dbc.Row(html.H1(children="Western Conference Standings", style=center_style)),
        dbc.Row(children=playoff_markers, style=center_style),
        html.Center(
            [
                html.Div(
                    [
                        dt.DataTable(
                            id="west_table",
                            columns=[
                                {"name": i, "id": i} for i in conf_table_cols("West")
                            ],
                            **conf_table_params,
                        )
                    ]
                )
            ]
        ),
        dbc.Row(html.H1(children="Eastern Conference Standings", style=center_style)),
        dbc.Row(children=playoff_markers, style=center_style),
        html.Center(
            [
                html.Div(
                    [
                        dt.DataTable(
                            id="east_table",
                            columns=[
                                {"name": i, "id": i} for i in conf_table_cols("East")
                            ],
                            **conf_table_params,
                        )
                    ]
                )
            ]
        ),
        dbc.Row(html.H1(children="League Standings", style=center_style)),
        dbc.Row(children=playoff_markers, style=center_style),
        html.Center(
            [
                html.Div(
                    [
                        dt.DataTable(
                            id="league_table",
                            columns=[
                                {"name": i, "id": i}
                                for i in conf_table_cols("Conference")
                            ],
                            **table_params,
                        )
                    ]
                )
            ]
        ),
    ]
)


@app.callback(Output("east_table", "data"), [Input("season_val", "value")])
def update_east_table(season_val):
    east = conf_table_data(season=season_val, conference="East")
    return east.to_dict("records")


@app.callback(Output("west_table", "data"), [Input("season_val", "value")])
def update_west_table(season_val):
    west = conf_table_data(season=season_val, conference="West")

    return west.to_dict("records")


@app.callback(Output("league_table", "data"), [Input("season_val", "value")])
def update_league_table(season_val):
    league = conf_table_data(season=season_val, conference="League")

    return league.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)
