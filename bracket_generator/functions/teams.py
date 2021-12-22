import glob
import numpy as np
import pandas as pd
import random
import mysql.connector
import datetime as datetime
import math
import os
import sys
from drs import drs

sys.path.append(os.path.abspath('..'))

# user = input("Username: ")
# password = input("Password: ")
#
# db = mysql.connector.connect(
#     host="localhost",
#     user=user,
#     passwd=password,
#     database="testdatabase"
# )

LTI = {"Legendary": [0, 2, 2, 4, 4, 6, 6],
       "Excellent": [0, 0, 2, 2, 4, 4, 6],
       "Very Good": [-2, 0, 0, 2, 2, 4, 4],
       "Good": [-2, -2, 0, 0, 2, 2, 4, ],
       "Average": [-4, -2, -2, 0, 0, 2, 2],
       "Below Average": [-4, -4, -2, -2, 0, 0, 2],
       "Bad": [-6, -4, -4, -2, -2, 0, 0]}

LTI_df = pd.DataFrame.from_dict(LTI, orient="index",
                                columns=["Legendary", "Excellent", "Very Good", "Good",
                                         "Average", "Below Average", "Bad"])


def rnd_rslt():
    return (random.randint(1, 6), random.randint(1, 6))


def team_rolls():
    return (rnd_rslt(), rnd_rslt(), rnd_rslt(), rnd_rslt(), rnd_rslt(), rnd_rslt(),
            rnd_rslt(), rnd_rslt(), rnd_rslt(), rnd_rslt(), rnd_rslt(), rnd_rslt())


def randNums(n, a, b, s):
    # finds n random ints in [a,b] with sum of s
    hit = False
    while not hit:
        total, count = 0, 0
        nums = []
        while total < s and count < n:
            r = random.randint(a, b)
            total += r
            count += 1
            nums.append(r)
        if total == s and count == n: hit = True
    return nums


def team_results(modifier, rolls):
    team = pd.DataFrame(rolls, columns=['Roll1', 'Roll2'])
    # Define + or minus for the modifier
    if modifier < 0:
        sign = -1
    else:
        sign = 1
    # Distribute values
    if abs(modifier) == 0:
        team.loc[:, 'Modifier'] = 0
    elif abs(modifier) < 12:
        team.loc[:, 'Modifier'] = randNums(12, 0, 1, abs(modifier))
    elif abs(modifier) < 24:
        team.loc[:, 'Modifier'] = randNums(12, 1, 2, abs(modifier))
    elif abs(modifier) < 36:
        team.loc[:, 'Modifier'] = randNums(12, 2, 3, abs(modifier))
    elif abs(modifier) < 48:
        team.loc[:, 'Modifier'] = randNums(12, 3, 4, abs(modifier))
    else:
        team.loc[:, 'Modifier'] = 4

    # Compute the final score
    team.loc[:, 'Modifier'] = team.loc[:, 'Modifier'] * sign
    team.loc[:, 'PointsScored'] = team['Roll1'] + team['Roll2'] + team['Modifier']
    team.loc[:, 'Score'] = team['PointsScored'].cumsum()
    return team


def match_results(home, away, home_rolls, away_rolls, home_offence, home_defense, away_offence, away_defence,
                  home_lti, away_lti):
    home_modifier = home_offence + away_defence + home_lti + 2
    away_modifier = away_offence + home_defense + away_lti - 2
    home_team = team_results(home_modifier, home_rolls)
    away_team = team_results(away_modifier, away_rolls)
    home_ot = rnd_rslt()
    away_ot = rnd_rslt()
    for i in range(10):
        if 11 + i in home_team.index:
            if home_team.loc[11 + i, 'Score'] == away_team.loc[11 + i, 'Score']:
                home_team.loc[12 + i, 'Roll1'] = home_ot[0]
                home_team.loc[12 + i, 'Roll2'] = home_ot[1]
                home_team.loc[12 + i, 'PointsScored'] = home_team.loc[12 + i, 'Roll1'] + home_team.loc[12 + i, 'Roll2']
                home_team.loc[:, 'Score'] = home_team['PointsScored'].cumsum()
                away_team.loc[12 + i, 'Roll1'] = away_ot[0]
                away_team.loc[12 + i, 'Roll2'] = away_ot[1]
                away_team.loc[12 + i, 'PointsScored'] = away_team.loc[12 + i, 'Roll1'] + away_team.loc[12 + i, 'Roll2']
                away_team.loc[:, 'Score'] = away_team['PointsScored'].cumsum()
    return {home: home_team, away: away_team}


def round_results(matches, LTI_df, home_rolls=None, away_rolls=None):
    results = {}
    for match in matches:
        if (home_rolls is None) and (away_rolls is None):
            results[str(match)] = match_results(match[0], match[1], team_rolls(), team_rolls(),
                                                teams.loc[match[0], 'offense'], teams.loc[match[0], 'defence'],
                                                teams.loc[match[1], 'offense'], teams.loc[match[1], 'defence'],
                                                LTI_df.loc[teams.loc[match[0], 'LTI'], teams.loc[match[1], 'LTI']],
                                                LTI_df.loc[teams.loc[match[1], 'LTI'], teams.loc[match[0], 'LTI']])
        elif home_rolls is None:
            results[str(match)] = match_results(match[0], match[1], team_rolls(), away_rolls,
                                                teams.loc[match[0], 'offense'], teams.loc[match[0], 'defence'],
                                                teams.loc[match[1], 'offense'], teams.loc[match[1], 'defence'],
                                                LTI_df.loc[teams.loc[match[0], 'LTI'], teams.loc[match[1], 'LTI']],
                                                LTI_df.loc[teams.loc[match[1], 'LTI'], teams.loc[match[0], 'LTI']])
        elif away_rolls is None:
            results[str(match)] = match_results(match[0], match[1], home_rolls, team_rolls(),
                                                teams.loc[match[0], 'offense'], teams.loc[match[0], 'defence'],
                                                teams.loc[match[1], 'offense'], teams.loc[match[1], 'defence'],
                                                LTI_df.loc[teams.loc[match[0], 'LTI'], teams.loc[match[1], 'LTI']],
                                                LTI_df.loc[teams.loc[match[1], 'LTI'], teams.loc[match[0], 'LTI']])
        else:
            results[str(match)] = match_results(match[0], match[1], home_rolls, away_rolls,
                                                teams.loc[match[0], 'offense'], teams.loc[match[0], 'defence'],
                                                teams.loc[match[1], 'offense'], teams.loc[match[1], 'defence'],
                                                LTI_df.loc[teams.loc[match[0], 'LTI'], teams.loc[match[1], 'LTI']],
                                                LTI_df.loc[teams.loc[match[1], 'LTI'], teams.loc[match[0], 'LTI']])
    return results


def get_players_scores(scoring_lookup, rolls, modifier=None):
    players_scores = pd.DataFrame()
    for r in rolls:
        tmp = scoring_lookup.loc[(scoring_lookup['Roll1'] == r[0]) & (scoring_lookup['Roll2'] == r[1])]
        players_scores = pd.concat([players_scores, tmp])
    players_scores.reset_index(inplace=True, drop=True)
    if modifier is None:
        players_scores.loc[:, 'MOD'] = 0
    else:
        players_scores.loc[:, 'MOD'] = modifier
    return players_scores


def get_player_stats(players_scores, players):
    players_stats = pd.DataFrame(0, index=players.loc[:, 'Player'],
                                 columns=['FG', 'FGA', 'ORB', 'DRB', 'AST'])
    for i in players_scores.index:
        players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] = \
            players_scores.loc[i, 'Points1'] + players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG']
        players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] = \
            players_scores.loc[i, 'Points2'] + players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG']
        players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FGA'] = \
            players_scores.loc[i, 'FGA1'] + players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FGA']
        players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FGA'] = \
            players_scores.loc[i, 'FGA2'] + players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FGA']
        players_stats.loc[players_scores.loc[i, 'RB_Player1'], 'ORB'] = \
            players_scores.loc[i, 'Rebounds1'] + players_stats.loc[players_scores.loc[i, 'RB_Player1'], 'ORB']
        players_stats.loc[players_scores.loc[i, 'RB_Player2'], 'DRB'] = \
            players_scores.loc[i, 'Rebounds2'] + players_stats.loc[players_scores.loc[i, 'RB_Player2'], 'DRB']
        players_stats.loc[players_scores.loc[i, 'AS_Player1'], 'AST'] = \
            players_scores.loc[i, 'Assists1'] + players_stats.loc[players_scores.loc[i, 'AS_Player1'], 'AST']
        players_stats.loc[players_scores.loc[i, 'AS_Player2'], 'AST'] = \
            players_scores.loc[i, 'Assists2'] + players_stats.loc[players_scores.loc[i, 'AS_Player2'], 'AST']
        if (players_scores.loc[i, 'MOD'] == 1) or (players_scores.loc[i, 'MOD'] == 2):
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] + players_scores.loc[i, 'MOD']
        elif players_scores.loc[i, 'MOD'] == 3:
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] + 2
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] + 1
        elif players_scores.loc[i, 'MOD'] == 4:
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] + 2
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] + 2
        elif (players_scores.loc[i, 'MOD'] == -1) or (players_scores.loc[i, 'MOD'] == -2):
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] + players_scores.loc[i, 'MOD']
        elif players_scores.loc[i, 'MOD'] == -3:
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] - 2
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] - 1
        elif players_scores.loc[i, 'MOD'] == -4:
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'FG'] - 2
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'FG'] - 2
    return players_stats


def assign_assists(df, i, points_col='Points2', assits_col='Assists1'):
    if ((df.loc[i, points_col] - 2) % 2 == 0) and ((df.loc[i, points_col] - 2) > 0):
        df.loc[i, assits_col] = (df.loc[i, points_col] - 2) / 2
    if ((df.loc[i, points_col]) % 3 == 0) and ((df.loc[i, points_col]) > 0):
        df.loc[i, assits_col] = df.loc[i, assits_col] + (df.loc[i, points_col] - 3) / 3
    if ((df.loc[i, points_col]) % 5 == 0) and ((df.loc[i, points_col]) > 4) and (df.loc[i, points_col] != 10):
        df.loc[i, assits_col] = df.loc[i, assits_col] + (df.loc[i, points_col]) / 5
    if ((df.loc[i, points_col]) % 7 == 0) and ((df.loc[i, points_col]) > 6):
        df.loc[i, assits_col] = df.loc[i, assits_col] + (df.loc[i, points_col]) / 7 + 2
    if (df.loc[i, points_col]) % 11 == 0:
        df.loc[i, assits_col] = df.loc[i, assits_col] + 4
    return df


leagues = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Leagues.csv', index_col=0)
conferences = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Conferences.csv', index_col=0)
divisions = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Divisions.csv', index_col=0)
teams = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Teams.csv', index_col=0)
schedule = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Schedule.csv', index_col=0)

# players = pd.DataFrame({'Player': ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10'],
#                         'Position': ['C', 'G', 'G', 'F', 'F', 'C', 'G', 'G', 'F', 'F'],
#                         'Points1': [9, 7, 3, 5, 2, 3, 2, 1, 1, 1],
#                         'Points2': [11, 7, 4, 2, 3, 2, 2, 1, 2, 2],
#                         'Rebounds1': [9, 3, 4, 2, 2, 4, 1, 1, 1, 1],
#                         'Rebounds2': [10, 3, 6, 3, 3, 5, 2, 1, 1, 2],
#                         'Assists1': [10, 7, 1, 2, 1, 1, 9, 1, 1, 0],
#                         'Assists2': [1, 2, 0, 2, 1, 3, 3, 1, 0, 0]})

players_df = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Players.csv')
players = {}
for i in teams.index:
    players[i] = players_df.loc[players_df['Team'] == i]

roll1 = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6]
roll2 = [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6]
fg1 = [0, 1, 0, 2, 4, 2, 1, 2, 1, 4, 3, 4, 2, 3, 2, 4, 3, 5, 3, 3, 3, 5, 3, 5, 2, 1, 4, 4, 4, 5, 4, 3, 4, 4, 5, 5]
fg2 = [2, 2, 4, 3, 2, 5, 2, 2, 4, 2, 4, 4, 2, 2, 4, 3, 5, 4, 2, 3, 4, 3, 6, 5, 4, 6, 4, 5, 6, 6, 3, 5, 5, 6, 6, 7]
rb1 = [1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 0, 1, 0, 1, 2, 2, 0, 0, 3, 2, 1, 2, 0, 1, 0, 3, 0, 2]
rb2 = [1, 2, 2, 3, 2, 2, 1, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 3, 4, 2, 3, 3, 3, 3, 2, 3, 2, 2, 2, 2, 4, 3, 3, 3, 3, 3]
as1 = [0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 2, 3, 2, 2, 2, 2, 3, 3, 2, 2, 2, 2, 3, 2, 2]
as2 = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 2, 0, 0, 1, 0, 1, 1]


def assign_random_lookup_stats(off_rbs, def_rbs, fga1, fga2):
    df = pd.DataFrame(
        {'roll1': roll1, 'roll2': roll2, 'Points1': 0, 'FGA1': 0, 'Points2': 0, 'FGA2': 0,
         'Rebounds1': 0, 'Rebounds2': 0,
         'Assists1': 0, 'Assists2': 0})
    for i in range(0, 36):
        fgs = randNums(2, 0, 12, df.loc[i, :].sum())
        df.loc[i, 'Points1'] = min(fgs[0], fgs[1])
        df.loc[i, 'Points2'] = max(fgs[0], fgs[1])
        df = assign_assists(df, i, points_col='Points2', assits_col='Assists1')
        df = assign_assists(df, i, points_col='Points1', assits_col='Assists2')
    k = 0
    rbs_11 = randNums(6, 5, 10, off_rbs)
    rbs_22 = randNums(6, 10, 20, def_rbs)
    fga_11 = randNums(6, 5, 12, fga1)
    fga_22 = randNums(6, 0, 5, fga2)
    for i in range(0, 6):
        rbs_1 = randNums(6, 0, 3, rbs_11[i])
        rbs_2 = randNums(6, 1, 4, rbs_22[i])
        if fga_11[i] != 0:
            fga_1 = randNums(6, 0, 3, fga_11[i])
        else:
            fga_1 = [0, 0, 0, 0, 0, 0]
        if fga_22[i] != 0:
            fga_2 = randNums(6, 0, 1, fga_22[i])
        else:
            fga_2 = [0, 0, 0, 0, 0, 0]
        for j in range(0, 6):
            df.loc[k, 'Rebounds1'] = min(rbs_1[j], rbs_1[j])
            df.loc[k, 'Rebounds2'] = max(rbs_2[j], rbs_2[j])
            df.loc[k, 'FGA1'] = df.loc[k, 'Points1'] + fga_1[j]
            df.loc[k, 'FGA2'] = df.loc[k, 'Points2'] + fga_2[j]
            k = k + 1
    return df.astype(int)


def get_scoring_lookup(lookup_stats, players):
    column_names = ['Roll1', 'Roll2',
                    'FG_Player1', 'Points1', 'FGA1', 'FG_Player2', 'Points2', 'FGA2',
                    'RB_Player1', 'Rebounds1', 'RB_Player2', 'Rebounds2',
                    'AS_Player1', 'Assists1', 'AS_Player2', 'Assists2']
    scoring_lookup = pd.DataFrame(columns=column_names)
    scoring_lookup.loc[:, 'Roll1'] = roll1
    scoring_lookup.loc[:, 'Roll2'] = roll2
    scoring_lookup.loc[:, 'Points1'] = lookup_stats.loc[:, 'Points1']
    scoring_lookup.loc[:, 'Points2'] = lookup_stats.loc[:, 'Points2']
    scoring_lookup.loc[:, 'FGA1'] = lookup_stats.loc[:, 'FGA1']
    scoring_lookup.loc[:, 'FGA2'] = lookup_stats.loc[:, 'FGA2']
    scoring_lookup.loc[:, 'Rebounds1'] = lookup_stats.loc[:, 'Rebounds1']
    scoring_lookup.loc[:, 'Rebounds2'] = lookup_stats.loc[:, 'Rebounds2']
    scoring_lookup.loc[:, 'Assists1'] = lookup_stats.loc[:, 'Assists1']
    scoring_lookup.loc[:, 'Assists2'] = lookup_stats.loc[:, 'Assists2']
    for col in ['FG_Player1', 'RB_Player1', 'AS_Player1']:
        for c in ['Points1', 'Rebounds1', 'Assists1']:
            tmp = players.sample(n=36, weights=c, random_state=1, replace=True)
            tmp.reset_index(inplace=True)
        for r in tmp.index:
            draw_p2 = players.drop(players[players['Player'] == tmp.loc[r, 'Player']].index).sample(n=1,
                                                                                                    weights='Points2')
            draw_r2 = players.drop(players[players['Player'] == tmp.loc[r, 'Player']].index).sample(n=1,
                                                                                                    weights='Rebounds2')
            draw_a2 = players.drop(players[players['Player'] == tmp.loc[r, 'Player']].index).sample(n=1,
                                                                                                    weights='Assists2')
            scoring_lookup.loc[r, 'FG_Player2'] = draw_p2.iloc[0, 0]
            scoring_lookup.loc[r, 'RB_Player2'] = draw_r2.iloc[0, 0]
            scoring_lookup.loc[r, 'AS_Player2'] = draw_a2.iloc[0, 0]

        scoring_lookup.loc[:, col] = tmp.loc[:, 'Player']
    return scoring_lookup


def assign_positions(detailed_stats, players, team):
    for p in detailed_stats.index:
        detailed_stats.loc[p, 'Position'] = players[team].loc[players[team]['Player'] == p, ['Position']]
    return detailed_stats

a = {}
scoring_lookup = {}
for i in teams.index:
    a[i] = assign_random_lookup_stats(off_rbs=40 + round(teams.loc[i, 'offense'] / 4),
                                      def_rbs=80 - round(teams.loc[i, 'defence'] / 2),
                                      fga1=50 - round(teams.loc[i, 'offense'] / 4),
                                      fga2=20 - round(teams.loc[i, 'offense'] / 5))
    scoring_lookup[i] = get_scoring_lookup(a[i], players[i])

path = 'E:\\Projects\\Github\\bracket_generator\\database/Test/Rolls/'
all_files = {}
rolls = {}
for i in range(12):
    all_files[i] = glob.glob(path + 'Round_' + str(i) + '/' + "*.csv")
    rolls[i] = {}
    for j in range(4):
        name = all_files[i][j]
        name = name.replace(path + 'Round_' + str(i) + '\\', '').replace(".csv", '')
        tmp = pd.read_csv(all_files[i][j])
        tms = name.split(' .vs ')
        rolls[i][name] = {}
        rolls[i][name][tms[0]] = tmp.loc[:, ['HomeRoll1', 'HomeRoll2']]
        rolls[i][name][tms[1]] = tmp.loc[:, ['AwayRoll1', 'AwayRoll2']]

import_results = True
matches = {}
detailed_results = {}
headers = ['Round', 'Home Team', 'Away Team', 'Home F/T Points', 'Away F/T Points', 'Home H/T Points',
           'Away H/T Points', 'OT']
results = pd.DataFrame(columns=headers)
players_detailed_statistics = {}
cntr = 0
for i in schedule.index:
    matches[i] = []
    detailed_results[i] = {}
    for j in schedule.columns:
        cntr = cntr + 1
        detailed_results[i][int(j)] = {}
        temp = iter(schedule.loc[i, j].split(" .vs "))
        res = [(ele, next(temp)) for ele in temp]
        matches[i].append(res)
        home_rolls = tuple(rolls[i][schedule.loc[i, j]][res[0][0]].itertuples(index=False, name=None))
        away_rolls = tuple(rolls[i][schedule.loc[i, j]][res[0][1]].itertuples(index=False, name=None))
        if import_results is True:
            detailed_results[i][int(j)] = round_results(matches[i][int(j)], LTI_df, home_rolls, away_rolls)
        else:
            detailed_results[i][int(j)] = round_results(matches[i][int(j)], LTI_df)
        results.loc[cntr, 'Round'] = i + 1
        results.loc[cntr, 'Home Team'] = res[0][0]
        results.loc[cntr, 'Away Team'] = res[0][1]
        results.loc[cntr, 'Home F/T Points'] = detailed_results[i][int(j)][str(res[0])][res[0][0]]['Score'].iat[-1]
        results.loc[cntr, 'Away F/T Points'] = detailed_results[i][int(j)][str(res[0])][res[0][1]]['Score'].iat[-1]
        results.loc[cntr, 'Home H/T Points'] = detailed_results[i][int(j)][str(res[0])][res[0][0]]['Score'].iat[5]
        results.loc[cntr, 'Away H/T Points'] = detailed_results[i][int(j)][str(res[0])][res[0][1]]['Score'].iat[5]
        if detailed_results[i][int(j)][str(res[0])][res[0][0]]['Score'].iat[11] == \
                detailed_results[i][int(j)][str(res[0])][res[0][1]]['Score'].iat[11]:
            results.loc[cntr, 'OT'] = 'Yes'
        if i == 0:
            players_detailed_statistics[res[0][0]] = {}
            players_detailed_statistics[res[0][1]] = {}

        home_scores = \
            get_players_scores(scoring_lookup[res[0][0]],
                               tuple(detailed_results[i][int(j)][str(res[0])][res[0][0]].loc[:,
                                     ['Roll1', 'Roll2']].itertuples(index=False, name=None)),
                               modifier=list(detailed_results[i][int(j)][str(res[0])][res[0][0]]['Modifier']))
        away_scores = \
            get_players_scores(scoring_lookup[res[0][1]],
                               tuple(detailed_results[i][int(j)][str(res[0])][res[0][1]].loc[:,
                                     ['Roll1', 'Roll2']].itertuples(index=False, name=None)),
                               modifier=list(detailed_results[i][int(j)][str(res[0])][res[0][1]]['Modifier']))
        players_detailed_statistics[res[0][0]][i] = get_player_stats(home_scores, players[res[0][0]])
        players_detailed_statistics[res[0][1]][i] = get_player_stats(away_scores, players[res[0][1]])


players_statistics = {}
cols = ['Position', 'FG', 'FGA', 'FG%', 'ORB', 'DRB', 'TRB', 'AST','PTS/G','TRB/G','AST/G']
for i in players_detailed_statistics:
    for j in players_detailed_statistics[i]:
        if j == 0:
            players_statistics[i] = players_detailed_statistics[i][j]
        else:
            players_statistics[i] = players_statistics[i].add(players_detailed_statistics[i][j])
        for k in players_detailed_statistics[i][j].index:
            players_statistics[i].loc[k,'Position'] = players[i].loc[players[i]['Player'] == k, 'Position'].values
    players_statistics[i].loc[:, 'TRB'] = players_statistics[i].loc[:, 'ORB'] + players_statistics[i].loc[:, 'DRB']
    players_statistics[i].loc[:, 'FG%'] = players_statistics[i].loc[:, 'FG'] / 2 / players_statistics[i].loc[:, 'FGA']
    players_statistics[i].loc[:, 'PTS/G'] = players_statistics[i].loc[:, 'FG'] / (j+1)
    players_statistics[i].loc[:, 'TRB/G'] = players_statistics[i].loc[:, 'TRB'] / (j + 1)
    players_statistics[i].loc[:, 'AST/G'] = players_statistics[i].loc[:, 'AST'] / (j + 1)

    # players_statistics[i].loc[:, 'Team'] = i
    players_statistics[i] = players_statistics[i][cols]
    decimals = 2
    for c in ['PTS/G', 'TRB/G', 'AST/G']:
        players_statistics[i][c] = players_statistics[i][c].apply(lambda x: round(x, decimals))

players_standings = pd.concat(players_statistics, axis=0)
players_standings = players_standings.sort_values(by=['FG', 'FG%', 'TRB', 'AST'], ascending=False)

results[['Home F/T Points', 'Away F/T Points', 'Home H/T Points', 'Away H/T Points']] = results[
    ['Home F/T Points', 'Away F/T Points', 'Home H/T Points', 'Away H/T Points']].astype(int)

results.to_csv('E:\\Projects\\Github\\bracket_generator\\database\\Test/Results.csv', index=False)

for i in teams.index:
    tmp = players_statistics[i].sum()
    print('Team ' + i + ' AS: ' + str(round(tmp['AST'] / 11, 1)) + ' RB_OFF: ' + str(
        round(tmp['ORB'] / 11, 1)) + ' RB_DEF: ' + str(round(tmp['DRB'] / 11, 1)))

# # Define the cursor
# mycursor = db.cursor()
#
# mycursor.execute("DROP TABLE IF EXISTS Player")
# mycursor.execute("DROP TABLE IF EXISTS Results")
# mycursor.execute("DROP TABLE IF EXISTS Game")
# mycursor.execute("DROP TABLE IF EXISTS Team")
# mycursor.execute("DROP TABLE IF EXISTS Division")
# mycursor.execute("DROP TABLE IF EXISTS Conference")
# mycursor.execute("DROP TABLE IF EXISTS League")
#
# Q_League = "create table League (id varchar(4) primary key, name varchar(50))"
#
# Q_Conference = "create table Conference (id varchar(4) primary key, name varchar(50), LeagueId varchar(4)," \
#                "foreign key (LeagueId) references League(id))"
#
# Q_Division = "create table Division (id varchar(4) primary key, name varchar(50)," \
#              "LeagueId varchar(4), ConferenceId varchar(4)," \
#              "foreign key (LeagueId) references League(id)," \
#              "foreign key (ConferenceId) references Conference(id))"
#
# Q_Team = "create table Team (id varchar(3) primary key, name VARCHAR(50), offense tinyint, defense tinyint, " \
#          "LeagueId varchar(4), ConferenceId varchar(4), DivisionId varchar(4)," \
#          "foreign key (LeagueId) references League(id)," \
#          "foreign key (ConferenceId) references Conference(id)," \
#          "foreign key (DivisionId) references Division(id))"
#
# # TODO check if these are correct
# Q_Rolls = "create table Rolls (id int primary key auto_increment, TeamId varchar(3), " \
#           "Roll1 tinyint, Roll2 tinyint, Modifier tinyint, PointsScored tinyint, Score smallint, " \
#           "foreign key (TeamId) references Team(id))"
#
# Q_Results = "create table Results (gameId int primary key auto_increment, HomeTeamId varchar(3), AwayTeamId varchar(3)," \
#             "foreign key (HomeTeamId) references Team(id), " \
#             "foreign key (AwayTeamId) references Team(id), " \
#             "home_score_ft int default 0, away_score_ft int default 0)"
#
# Q_Player = "create table Player (playerId varchar(6) primary key, name varchar(50), TeamId varchar(3)," \
#            "foreign key (TeamId) references Team(id))"
#
# mycursor.execute(Q_League)
# mycursor.execute(Q_Conference)
# mycursor.execute(Q_Division)
# mycursor.execute(Q_Team)
# mycursor.execute(Q_Rolls)
# mycursor.execute(Q_Results)
# mycursor.execute(Q_Player)
#
# # Insert many values at once
# mycursor.executemany("insert into League (id, name) values (%s,%s)", leagues)
# db.commit()
# mycursor.executemany("insert into Conference (id, name, LeagueId) values (%s,%s,%s)", conferences)
# db.commit()
# mycursor.executemany("insert into Division (id, name, LeagueId, ConferenceId) values (%s,%s,%s,%s)", divisions)
# db.commit()
# mycursor.executemany(
#     "insert into Team (id, name, offense, defense, LeagueId, ConferenceId, DivisionId) values (%s,%s,%s,%s,%s,%s,%s)",
#     teams)
# db.commit()
# mycursor.executemany("insert into Game ()")
# mycursor.executemany("insert into Results (HomeTeamId, AwayTeamId, home_score_ft, away_score_ft) values (%s,%s,%s,%s)",
#                      match_results)
# db.commit()
# mycursor.executemany("insert into Player (playerId, name, TeamId) values (%s,%s,%s)", players)
# db.commit()

# mycursor.execute('describe Team')
# for x in mycursor:
#     print(x)
# # # Drop table
# mycursor.execute("DROP TABLE Player")
# mycursor.execute("DROP TABLE Results")
# mycursor.execute("DROP TABLE Team")

# # Create table
# mycursor.execute("CREATE TABLE Team (name VARCHAR(100), offence tinyint, defence tinyint,"
#                  "division VARCHAR(100), conference VARCHAR(100), league VARCHAR(100), "
#                  "teamID int PRIMARY KEY AUTO_INCREMENT)")

# # Alter the table by adding column
# mycursor.execute("alter table Test add column food varchar(50) not null")

# # Alter the table by dropping column
# mycursor.execute("alter table Test drop food")

# # Alter the table by changing the column name
# mycursor.execute("alter table Test change name first_name varchar(50)")
#
# # Describe the table
# mycursor.execute("describe Test")
# for x in mycursor:
#     print(x)

## Insert values into the table
# mycursor.execute("INSERT INTO Team (name, offence, defence, division, conference, league) VALUES (%s,%s,%s,%s,%s,%s)",
#                  ("TestTeam1", 12, -10, "Div1", "Cnf1", "Lgu1"))
# db.commit()

# mycursor.execute("CREATE TABLE Test (name varchar(50) not null, created datetime not null, gender enum('M', 'F', 'O'), id int primary key not null auto_increment)")
# mycursor.execute("insert into Test (name, created, gender) values (%s,%s,%s)", ("Joana", '2020-07-12', "F"))
# db.commit()

# Select data by specific column names
# * selects all columns
# where tells us the condition
# order by orders the data ascending or descending
# mycursor.execute("select * from Test where gender = 'M' order by id desc")
# mycursor.execute("select id, name from Test where gender = 'M' order by id desc")
#
#
#
# for x in mycursor:
#     print(x)

# # Insert many values at once
# mycursor.executemany("insert into Team (name, offense, defense, division, conference, league) values (%s,%s,%s,%s,%s,%s)", teams)

# class Team:
#     def __init__(self, name, offence, defence, division=None, conference=None, league=None):
#         self.name = name
#         self.offence = offence
#         self.defence = defence
#         self.division = division
#         self.conference = conference
#         self.league = league
#         self.W = self.L = self.pts = self.pa = 0
#
#     def game_result(self, pts, pa):
#         self.pts.append(pts)
#         self.pa.append(pa)
#
#
# league_size = 4
# team_names = ['A', 'B', 'C']
# teams = []
# for _ in team_names:
#     teams.append(Team(str(_),
#                       int(input('Team ' + str(_) + "'s offence level: ")),
#                       int(input('Team ' + str(_) + "'s defence level: ")),
#                       input('Team ' + str(_) + 's division :')))
#
# matches = {'AB': [100, 91],
#            'BC': [85, 92],
#            'CA': [90, 67]}
#
# # for match in matches:
#
#
#
#
# for team in teams:
#     print(team.name, team.offence, team.defence, team.division, team.conference)
#
