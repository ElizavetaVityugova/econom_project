import sqlite3
from datetime import datetime as dt
import pandas as pd
import logging as logger
logger.basicConfig(level=logger.INFO)
import numpy as np
import plotly.graph_objects as go


class Loader:
    def __init__(self):
        self.cache = []

    def __call__(self, input_league):
        logger.info(f'  ------------------------------------------')
        logger.info(f'  Starting load data from {input_league}')
        logger.info(f'  {dt.now()}')
        teams_data = pd.read_parquet(f"data/event_data/teams_{input_league}.parquet")
        events_data = pd.read_parquet(f"data/event_data/events_{input_league}.parquet")
        players_data = pd.read_parquet(f"data/event_data/players.parquet")
        create_teams_db(teams_data, input_league)
        create_events_db(events_data, input_league)
        create_players_db(players_data)
        saved_teams_amount = check_teams_db(input_league)[0]
        saved_events_amount = check_events_db(input_league)[0]
        saved_playrs_amount = check_players_db()[0]
        logger.info(f'  Loaded and saved {saved_teams_amount} teams')
        logger.info(f'  Loaded and saved {saved_events_amount} events')
        logger.info(f'  Loaded and saved {saved_playrs_amount} players')
        logger.info(f'  Data from {input_league} was loaded!')
        logger.info(f'  ------------------------------------------')
        self.cache.append(input_league)
        return True


class StatisticCollector:
    def __init__(self):
        self.cache = {}

    def __call__(self, input_league):
        logger.info(f'  ------------------------------------------')
        logger.info(f'Computing statistic for {input_league} ...')
        teams_data = get_data_for_teams_graph(input_league)
        passing_data = compute_teams_pass_statistic(input_league)
        shoting_data = compute_teams_shot_statistic(input_league)
        best_scorrers = get_best_scorers_data(input_league)
        best_assistants = get_best_assistants_data(input_league)
        self.cache[input_league] = (teams_data, passing_data,
                                    shoting_data, best_scorrers,
                                    best_assistants)
        logger.info(f'Statistic for {input_league} was computed!')
        logger.info(f'  ------------------------------------------')
        return self.cache[input_league]


def create_teams_db(data, league):
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    league = f"{league}_teams"
    query = f'CREATE TABLE IF NOT EXISTS {league} ( \
           id              INTEGER UNIQUE NOT NULL PRIMARY KEY, \
           team_name            TEXT NOT NULL, \
           position               INTEGER,\
           goals               INTEGER, \
           points               INTEGER, \
           goalsDiff               INTEGER \
       );'
    cur_data.execute(query)

    for id, name, position, goals, points, goalsdiff in zip(data.teamId, data.teamName,
                                                            data.position, data.goals,
                                                            data.points, data.goalsDiff ):
        query = f'INSERT OR IGNORE INTO {league} (id, team_name, position, ' \
                f'goals, points, goalsDiff) VALUES ( ?,?,?,?,?,?)'
        params = (id, name, position, goals, points, goalsdiff)
        cur_data.execute(query, params)

    conn_data.commit()
    conn_data.close()


def create_events_db(data, league):
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    league = f"{league}_events"
    team_league = f"{league}_teams"
    query = f'CREATE TABLE IF NOT EXISTS {league} ( \
           id              INTEGER UNIQUE NOT NULL PRIMARY KEY, \
           matchId            INTEGER NOT NULL, \
           eventSec               REAL,\
           eventName               TEXT NOT NULL, \
           teamId               INTEGER NOT NULL, \
           playerId               INTEGER, \
           playerName              TEXT NOT NULL, \
           accurate             BOOLEAN, \
           goal                BOOLEAN, \
           assist               BOOLEAN,\
           keyPass             BOOLEAN,\
           FOREIGN KEY(teamId) REFERENCES  {team_league}(id) \
       );'
    cur_data.execute(query)
    for id, match_id, eventSec, eventName,\
        teamId, playerId, playerName, accurate, goal, assist, keyPass in zip(data.id, data.matchId, data.eventSec,
                                                                             data.eventName, data.teamId,
                                                                             data.playerId, data.playerName,
                                                                             data.accurate, data.goal, data.assist,
                                                                             data.keyPass):
        query = f'INSERT OR IGNORE INTO {league} (id, matchId, eventSec, ' \
                f'eventName, teamId, playerId,playerName, accurate, goal, assist, keyPass) ' \
                f'VALUES ( ?,?,?,?,?,?,?,?,?,?,?)'
        params = (id, match_id, eventSec, eventName,
                  teamId, playerId, playerName,  accurate,
                  goal, assist, keyPass)
        cur_data.execute(query, params)

    conn_data.commit()
    conn_data.close()


def create_players_db(data):
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    query = f'CREATE TABLE IF NOT EXISTS players ( \
           id              INTEGER UNIQUE NOT NULL PRIMARY KEY, \
           strong_foot            TEXT NOT NULL, \
           player_name               TEXT NOT NULL,\
           player_position               TEXT NOT NULL \
       );'
    cur_data.execute(query)
    for player_id, strong_foot, player_name, player_position in zip(data.playerId, data.playerStrongFoot,
                                                                   data.playerName, data.playerPosition):
        query = f'INSERT OR IGNORE INTO players (id, strong_foot, player_name, ' \
                f'player_position) VALUES ( ?,?,?,?)'
        params = (player_id, strong_foot, player_name, player_position)
        cur_data.execute(query, params)

    conn_data.commit()
    conn_data.close()


def get_best_scorers_data(league):
    league = f"{league}_events"
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    query =f'select players.id , players.player_name,  count(eventName) as shot_amount, teamId'\
           f' from {league} join players on {league}.playerId = players.id' \
           f' where eventName="Shot" and goal=1  group by players.id order by shot_amount desc limit 20;'
    print(query)
    result = cur_data.execute(query).fetchall()
    data = pd.DataFrame(result, columns=['player_id', 'player_name', 'goals_amount', 'team_id'])
    return data


def get_best_assistants_data(league):
    league = f"{league}_events"
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    query =f'select players.id , players.player_name,  count(eventName) as assist_amount, teamId'\
           f' from {league} join players on {league}.playerId = players.id' \
           f' where eventName="Pass" and assist=1  group by players.id order by assist_amount desc limit 20;'
    print(query)
    result = cur_data.execute(query).fetchall()
    data = pd.DataFrame(result, columns=['player_id', 'player_name', 'assist_amount', 'team_id'])
    return data


def get_team_name_by_id(id, league):
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    league = f"{league}_teams"
    query = f"select team_name from {league} where id={id};"
    result = cur_data.execute(query).fetchone()
    return result


def get_data_for_teams_graph(league):
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    league = f"{league}_teams"
    query = f"select team_name, position, points, goals from {league} order by position;"
    result = cur_data.execute(query).fetchall()
    df = pd.DataFrame(result, columns=['team_name', 'position', 'points', 'goals'])
    return df


#select players.id ,players.player_name,  count(eventName)  as shots_amount  from events_england join players on events_england.playerId = players.id where eventName="Shot" and accurate=1 group by players.id order by shots_amount desc ;
def _compute_total_accurate_passes_amount(league_events, league_teams):
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    query = f'select teamId, position, points, goals, {league_teams}.team_name, ' \
            f'count(accurate), count(distinct(matchId)) from {league_events} '\
            f'join {league_teams} on {league_teams}.id = {league_events}.teamID  ' \
            'where accurate=1 and eventName="Pass" group by teamId;'
    result = cur_data.execute(query).fetchall()
    data = pd.DataFrame(result, columns=['id', 'position', 'points', 'goals',
                                         'team_name', 'accurate_pass_amount', 'match_amount'])
    return data


def _compute_total_accurate_shots_amount(league_events, league_teams):
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    query = f'select teamId, position, points, goals, {league_teams}.team_name, ' \
            f'count(accurate), count(distinct(matchId)) from {league_events} '\
            f'join {league_teams} on {league_teams}.id = {league_events}.teamID  ' \
            'where accurate=1 and eventName="Shot" group by teamId;'
    result = cur_data.execute(query).fetchall()
    data = pd.DataFrame(result, columns=['id', 'position', 'points', 'goals',
                                         'team_name', 'accurate_shots_amount', 'match_amount'])
    return data


def compute_teams_pass_statistic(league):
    league_event = f"{league}_events"
    league_teams = f"{league}_teams"
    df_accurate_passes = _compute_total_accurate_passes_amount(league_event, league_teams)
    df_accurate_passes["accurate_passes_per_match"] = np.round(df_accurate_passes["accurate_pass_amount"] /
                                                               df_accurate_passes["match_amount"], 0)
    df_accurate_passes.sort_values("accurate_passes_per_match", inplace=True)
    return df_accurate_passes


def compute_teams_shot_statistic(league):
    league_event = f"{league}_events"
    league_teams = f"{league}_teams"
    df_accurate_shots = _compute_total_accurate_shots_amount(league_event, league_teams)
    df_accurate_shots["accurate_shots_per_match"] = np.round(df_accurate_shots["accurate_shots_amount"] /
                                                             df_accurate_shots["match_amount"], 0)
    df_accurate_shots.sort_values("accurate_shots_per_match", inplace=True)
    return df_accurate_shots



def check_teams_db(league):
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    table_name = f"{league}_teams"
    params = (table_name,)
    query = 'SELECT count(*) FROM sqlite_master WHERE type="table"  AND name=?'
    ret = cur_data.execute(query, params).fetchone()
    if not ret[0]:
        return [0]
    query = f'SELECT COUNT(*) FROM {table_name}'
    ret = cur_data.execute(query).fetchone()
    conn_data.close()
    return ret


def check_events_db(league):
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    table_name = f"{league}_events"
    params = (table_name,)
    query = 'SELECT count(*) FROM sqlite_master WHERE type="table"  AND name=?'
    ret = cur_data.execute(query, params).fetchone()
    if not ret[0]:
        return [0]
    query = f'SELECT COUNT(*) FROM {table_name}'
    ret = cur_data.execute(query).fetchone()
    conn_data.close()
    return ret


def check_players_db():
    conn_data = sqlite3.connect('databases/soccer_data.sqlite')
    cur_data = conn_data.cursor()
    query = 'SELECT count(*) FROM sqlite_master WHERE type="table"  AND name="players"'
    ret = cur_data.execute(query).fetchone()
    if not ret[0]:
        return [0]
    query = f'SELECT COUNT(*) FROM players'
    ret = cur_data.execute(query).fetchone()
    conn_data.close()
    return ret
