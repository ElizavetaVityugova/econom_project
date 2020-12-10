import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app
import utils
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

league_tab_mapping = {
    'tab-1': 'england',
    'tab-2': 'france',
    'tab-3': 'spain',
    'tab-4': 'germany',
    'tab-5': 'italy',
}

loader = utils.Loader()
statistic_collector = utils.StatisticCollector()

layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Teams Analysis", href='/apps/app1')),
            dbc.NavItem(dbc.NavLink("Players Analysis", href='/apps/app2')),
        ],
        brand="Soccer Analysis",
        brand_href="/",
        color="dark",
        dark=True,
    ),
    html.B(),
    html.H2('Teams analysis', title="Analysis of the each ligue"),
    dcc.Tabs(id='tabs-example', value='tab-2', children=[
            dcc.Tab(label='England', value='tab-1'),
            dcc.Tab(label='France', value='tab-2'),
            dcc.Tab(label='Spain', value='tab-3'),
            dcc.Tab(label='Germany', value='tab-4'),
            dcc.Tab(label='Italy', value='tab-5'),
        ]),
    html.Div(id='indicator-graphic-teams')
])


@app.callback(Output('indicator-graphic-teams', 'children'),
              Input(component_id='tabs-example', component_property='value'))
def render_content(tab):
    if league_tab_mapping[tab] not in loader.cache:
        loader(input_league=league_tab_mapping[tab])
    if league_tab_mapping[tab] not in statistic_collector.cache.keys():
        table_teams, passing_data, shoting_data, _, _ = statistic_collector(league_tab_mapping[tab])
    else:
        table_teams, passing_data, shoting_data, _, _ = statistic_collector.cache[league_tab_mapping[tab]]
    goals_bar = px.bar(table_teams, x='team_name', y='goals', text='position', color='points', title="Goals by team")
    goals_bar.update_layout(xaxis={'categoryorder': 'total descending'})

    accurate_passes_amount_bar = px.bar(passing_data, x="team_name", y="accurate_passes_per_match",
                                        text="position", title="Accurate Passes  by team", color="points")
    accurate_shots_amount_bar = px.bar(shoting_data, x="team_name", y="accurate_shots_per_match",
                                       text="position", title="Accurate Shots  by team", color="points")
    accurate_shots_amount_bar.update_layout(transition_duration=500)
    accurate_passes_amount_bar.update_layout(transition_duration=500)

    goals_points_corr = px.scatter(passing_data, x="goals", y="points", trendline="ols")
    passes_points_corr = px.scatter(passing_data, x="accurate_passes_per_match", y="points", trendline="ols")
    shots_points_corr = px.scatter(shoting_data, x="accurate_shots_per_match", y="points", trendline="ols")
    parralel_data = pd.concat([passing_data, shoting_data["accurate_shots_per_match"]], axis=1)
    parrallel_figure = px.parallel_coordinates(parralel_data, color="points",
                                               dimensions=["accurate_passes_per_match", "accurate_shots_per_match",
                                                           "goals", "position"],
                                               labels={"accurate_passes_per_match": "Accurate Passes amount per game",
                                                       "accurate_shots_per_match": "Accurate Shot amount per game",
                                                       "goals": "Goals Amount",
                                                       "position": "Result Position"},
                                                        color_continuous_scale=px.colors.diverging.Tealrose,
                                                        color_continuous_midpoint=1)
    parrallel_figure.update_layout(transition_duration=500)
    results_table = go.Figure(data=[
        go.Table(
            header=dict(values=['Position', 'Team Name', 'Points'],
                        fill_color='paleturquoise',
                        align='left',
                        height=20),
            cells=dict(values=[table_teams.position, table_teams.team_name, table_teams.points],
                       fill_color='lavender',
                       align='left',
                       font_size=14,
                       height=30))
    ])
    results_table.update_layout(xaxis={'categoryorder': 'total descending'}, transition_duration=500)
    correlations = dbc.Row([dbc.Col(dcc.Graph(figure=goals_points_corr)),
                            dbc.Col(dcc.Graph(figure=passes_points_corr)),
                            dbc.Col(dcc.Graph(figure=shots_points_corr))])
    graph = html.Div(
        children=[
                    dcc.Graph(figure=results_table),
                    dcc.Graph(figure=goals_bar),
                    dcc.Graph(figure=parrallel_figure),
                    correlations,
                    dcc.Graph(figure=accurate_passes_amount_bar),
                    dcc.Graph(figure=accurate_shots_amount_bar)
        ],
    )

    return graph

