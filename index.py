import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from apps import app1, app2

app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


LOGO = "/assets/logo.png"

first_card = dbc.Card(
    [
        dbc.CardImg(src="/assets/soccer_data_analysis.jpeg", top=True),
        dbc.CardBody(
            [
                html.H4("About", className="card-title"),
                html.P(
                    "This project is designed to visualize football data in order to make the process "
                    "of studying it more interesting and exciting,"
                    "and  possibly to find out what the results of teams depend on.",
                    className="card-text",
                ),
                dbc.Button("Github link", color="primary", href="https://github.com/ElizavetaVityugova/econom_project"),
            ]
        ),
    ],
    style={
        "width": "20rem",
        "margin-left": "200px",
        "margin-top": "50px"},
)

second_card = dbc.Card(
    [
        dbc.CardImg(src="/assets/data.jpg", top=True),
        dbc.CardBody(
            [
                html.H4("Dataset", className="card-title"),
                html.P(
                    "The largest open collection of soccer-logs ever released, collected by Wyscout "
                    "containing all the spatio-temporal events: passes, shots, fouls, etc."
                    "that occur during all matches of an entire season of seven competitions:  ",
                    className="card-text",
                ),
                html.Ol(children=[
                    html.Li('La Liga'),
                    html.Li('Serie A'),
                    html.Li('Bundesliga'),
                    html.Li('Premier League'),
                    html.Li('Ligue 1'),
                    html.Li('FIFA World Cup 2018'),
                    html.Li('UEFA')
                ]),
                html.Br(),
                dbc.Button("Dataset Link", color="info", href='https://figshare.com/collections/Soccer_match_event_dataset/4415000/5'),
            ]
        ),
    ],
    style={
        "width": "20rem",
        "margin-top": "50px"},
)

third_card = dbc.Card(
    [
        dbc.CardImg(src="/assets/user_guide.jpg", top=True),
        dbc.CardBody(
            [
                html.H4("User manual", className="card-title"),
                html.Ol(children=[
                    html.Li('To see data about teams choose "Team Analysis" in Navigation Menu.'),
                    html.Li('To see data about players choose "Player Analysis" in Navigation Menu.'),
                ]),
            ]
        ),
    ],
    style={
        "width": "20rem",
        "margin-top": "50px"},
)

thourd_card = dbc.Card(
    [
        dbc.CardImg(src="/assets/db_schema.png", top=True),
        dbc.CardBody(
            [
                html.H4("DB Schema", className="card-title"),
                html.P(
                    "The schema of our project database",
                    className="card-text",
                ),
            ]
        ),
    dbc.Button("Database Schema image", color="secondary", href="")
    ],
    style={
        "width": "40rem",
        "margin-top": "50px"},
)
cards = dbc.Row([dbc.Col(first_card, width="auto"),
                 dbc.Col(second_card, width="auto"),
                 dbc.Col(third_card, width="auto"),
                 dbc.Col(thourd_card, width="auto")])



index_page = html.Div(children=[
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Team Analysis", href='/apps/app1')),
            dbc.NavItem(dbc.NavLink("Player Analysis", href='/apps/app2')),
        ],
        brand="Soccer Analysis",
        brand_href="/",
        color="dark",
        dark=True,
    ),
    cards
],
    style={
        "background-image": 'url(/assets/field.jpg)',
        "background-repeat": "no-repeat",
        "background-position": "center",
        "background-size": "cover",
        "position": "fixed",
	    "min-height": "100%",
	    "min-width": "100%",}
)


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
    else:
        return index_page


if __name__ == '__main__':
    app.run_server(debug=True)
