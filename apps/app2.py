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


best_scorrer = dbc.Card(
    [
        dbc.CardImg(src="/assets/scorrers.jpg", top=True),
        dbc.CardBody(
            [
                html.H4("Top 20 Scorers", className="card-title"),
                html.P(
                    "The table represent top 20 scorer in this league",
                    className="card-text",
                )
            ]
        ),
    ],
    style={"width": "20rem",
           "margin-left":"200px",
           "margin-top": "50px"},
)

best_passer = dbc.Card(
    [
        dbc.CardImg(src="/assets/best_passer.jpg", top=True),
        dbc.CardBody(
            [
                html.H4("Top 20 Assistant", className="card-title"),
                html.P(
                    "The table represent top 20 passer  in this league."
                    "This means that the player gave an assist",
                    className="card-text",
                )
            ]
        ),
    ],
    style={"width": "20rem",
           "margin-left": "200px",
           "margin-top": "100px"},
)

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
    html.H2('Players analysis', title="Analysis of the each ligue"),
    dcc.Tabs(id='tabs-example', value='tab-2', children=[
            dcc.Tab(label='England', value='tab-1'),
            dcc.Tab(label='France', value='tab-2'),
            dcc.Tab(label='Spain', value='tab-3'),
            dcc.Tab(label='Germany', value='tab-4'),
            dcc.Tab(label='Italy', value='tab-5'),
        ]),
    html.Div(id='indicator-graphic-players')
])



@app.callback(Output('indicator-graphic-players', 'children'),
              Input(component_id='tabs-example', component_property='value'))
def render_content(tab):
    if league_tab_mapping[tab] not in loader.cache:
        loader(input_league=league_tab_mapping[tab])
    if league_tab_mapping[tab] not in statistic_collector.cache.keys():
        _, _, _, best_scorrers, best_assistants = statistic_collector(league_tab_mapping[tab])
    else:
        _, _, _, best_scorrers, best_assistants = statistic_collector.cache[league_tab_mapping[tab]]
    position_scorers = [i for i in range(1, len(best_scorrers)+1)]
    position_assistants = [i for i in range(1, len(best_assistants) +1)]

    results_table_scorers = go.Figure(data=[
        go.Table(
            header=dict(values=['Position', 'Player Name', 'Goals Amount', 'Team Id'],
                        fill_color='paleturquoise',
                        align='left',
                        height=20),
            cells=dict(values=[position_scorers, best_scorrers.player_name,
                               best_scorrers.goals_amount, best_scorrers.team_id],
                       fill_color='lavender',
                       align='left',
                       font_size=14,
                       height=30))
    ])

    results_table_assitants = go.Figure(data=[
        go.Table(
            header=dict(values=['Position', 'Player Name', 'Assist Amount', 'Team Id'],
                        fill_color='paleturquoise',
                        align='left',
                        height=20),
            cells=dict(values=[position_assistants, best_assistants.player_name,
                               best_assistants.assist_amount, best_assistants.team_id],
                       fill_color='lavender',
                       align='left',
                       font_size=14,
                       height=30))
    ])
    results_table_scorers.update_layout(xaxis={'categoryorder': 'total descending'}, transition_duration=500)
    scorer_team_names = []
    for team_id in best_scorrers.team_id:
        try:
            team_name = str(utils.get_team_name_by_id(team_id, league_tab_mapping[tab])[0])
        except:
            team_name = str(utils.get_team_name_by_id(team_id, league_tab_mapping[tab]))
        scorer_team_names.append(f"Team Name: {team_name} - Team id: {team_id}")
    assistants_team_names = []
    for team_id in best_assistants.team_id:
        try:
            team_name = str(utils.get_team_name_by_id(team_id, league_tab_mapping[tab])[0])
        except:
            team_name = str(utils.get_team_name_by_id(team_id, league_tab_mapping[tab]))
        assistants_team_names.append(f"Team Name: {team_name} - Team id: {team_id}")
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
    assistants_fig = go.Figure(data=[go.Pie(labels=assistants_team_names, values=best_assistants.assist_amount)])
    assistants_fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                      marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    scorers_fig = go.Figure(data=[go.Pie(labels=scorer_team_names, values=best_scorrers.goals_amount)])
    scorers_fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                      marker=dict(colors=colors, line=dict(color='#000000', width=2)))

    scorers_visualization = dbc.Row([dbc.Col(best_scorrer, width="auto"),
                                     dbc.Col(dcc.Graph(figure=results_table_scorers), width="auto"),
                                     dbc.Col(dcc.Graph(figure=scorers_fig), width="auto")])
    assitants_visualization = dbc.Row([dbc.Col(best_passer, width="auto"),
                                       dbc.Col(dcc.Graph(figure=results_table_assitants), width="auto"),
                                       dbc.Col(dcc.Graph(figure=assistants_fig), width="auto")])
    graph = html.Div(
        children=[
            scorers_visualization,
            assitants_visualization
        ]
    )

    return graph
