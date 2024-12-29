import copy

from nba_data import table_cols, team_colors

center_style = {"textAlign": "center"}

table_params = dict(
    style_table={"overflowX": "scroll", "maxWidth": "80%", "minWidth": "40%"},
    style_header={
        "backgroundColor": "#D3D3D3",
        "fontWeight": "bold",
        "border": "1px solid black",
    },
    style_cell={
        "font-family": "sans-serif",
        "backgroundColor": "#E6E6E6",
        "textAlign": "center",
    },
    fixed_columns={"headers": True, "data": 2},
    style_data_conditional=[
        {
            "if": {
                "column_id": "Team",
                "filter_query": '{Team} contains "' + team + '"',
            },
            "backgroundColor": background_color,
            "border": "2px solid " + trim_color,
            "color": "white",
        }
        for team, background_color, trim_color in zip(
            team_colors.keys(),
            [team_colors[d][0] for d in team_colors],
            [team_colors[d][1] for d in team_colors],
        )
    ]
    + [
        {
            "if": {"filter_query": "{Difference} < 0.0", "column_id": "Difference"},
            "color": "red",
        },
        {
            "if": {"filter_query": "{Difference} > 0.0", "column_id": "Difference"},
            "color": "green",
        },
    ],
    style_cell_conditional=[
        {"if": {"column_id": "Record"}, "width": "75px"},
        {"if": {"column_id": "Rank"}, "width": "55px"},
    ]
    + [{"if": {"column_id": col}, "height": 31} for col in table_cols[2:]],
)

conf_table_params = copy.deepcopy(table_params)
conf_table_params["style_data_conditional"].append(
    {"if": {"filter_query": "{Rank} < 9", "column_id": "Rank"}, "fontWeight": "bold"}
)
