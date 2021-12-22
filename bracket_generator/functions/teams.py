import glob
import numpy as np
import pandas as pd
import random
import os
import sys

sys.path.append(os.path.abspath('..'))

roll1 = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6]
roll2 = [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6]

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
    return random.randint(1, 6), random.randint(1, 6)


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
                                 columns=['PTS', 'FGA', 'ORB', 'DRB', 'AST'])
    for i in players_scores.index:
        players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] = \
            players_scores.loc[i, 'Points1'] + players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS']
        players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] = \
            players_scores.loc[i, 'Points2'] + players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS']
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
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] + players_scores.loc[i, 'MOD']
        elif players_scores.loc[i, 'MOD'] == 3:
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] + 2
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] + 1
        elif players_scores.loc[i, 'MOD'] == 4:
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] + 2
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] + 2
        elif (players_scores.loc[i, 'MOD'] == -1) or (players_scores.loc[i, 'MOD'] == -2):
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] + players_scores.loc[i, 'MOD']
        elif players_scores.loc[i, 'MOD'] == -3:
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] - 2
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] - 1
        elif players_scores.loc[i, 'MOD'] == -4:
            players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player2'], 'PTS'] - 2
            players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] = \
                players_stats.loc[players_scores.loc[i, 'FG_Player1'], 'PTS'] - 2
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
    if ((df.loc[i, points_col]) % 11 == 0) and ((df.loc[i, points_col]) > 9):
        df.loc[i, assits_col] = df.loc[i, assits_col] + 4
    return df


def assign_players(players_df, teams):
    players = {}
    for i in teams.index:
        players[i] = players_df.loc[players_df['Team'] == i]
    return players


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


def assign_scoring_lookup(teams, players):
    a = {}
    df = {}
    for i in teams.index:
        a[i] = assign_random_lookup_stats(off_rbs=40 + round(teams.loc[i, 'offense'] / 4),
                                          def_rbs=80 - round(teams.loc[i, 'defence'] / 2),
                                          fga1=50 - round(teams.loc[i, 'offense'] / 4),
                                          fga2=20 - round(teams.loc[i, 'offense'] / 5))
        df[i] = get_scoring_lookup(a[i], players[i])
    return df


def load_team_rolls(path):
    # path = 'E:\\Projects\\Github\\bracket_generator\\database/Test/Rolls/'
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
    return rolls


## Load data
leagues = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Leagues.csv', index_col=0)
conferences = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Conferences.csv', index_col=0)
divisions = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Divisions.csv', index_col=0)
teams = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Teams.csv', index_col=0)
schedule = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Schedule.csv', index_col=0)
players_df = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Players.csv')
rolls = load_team_rolls('E:\\Projects\\Github\\bracket_generator\\database/Test/Rolls/')
# Process data
players = assign_players(players_df, teams)
scoring_lookup = assign_scoring_lookup(teams, players)


#TODO: Make a function
import_results = False
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

results[['Home F/T Points', 'Away F/T Points', 'Home H/T Points', 'Away H/T Points']] = results[
    ['Home F/T Points', 'Away F/T Points', 'Home H/T Points', 'Away H/T Points']].astype(int)

#TODO: Make a function
players_statistics = {}
cols = ['Position', 'PTS', 'FGA', 'FG%', 'ORB', 'DRB', 'TRB', 'AST','PTS/G','TRB/G','AST/G']
for i in players_detailed_statistics:
    for j in players_detailed_statistics[i]:
        if j == 0:
            players_statistics[i] = players_detailed_statistics[i][j]
        else:
            players_statistics[i] = players_statistics[i].add(players_detailed_statistics[i][j])
        for k in players_detailed_statistics[i][j].index:
            players_statistics[i].loc[k,'Position'] = players[i].loc[players[i]['Player'] == k, 'Position'].values
    players_statistics[i].loc[:, 'TRB'] = players_statistics[i].loc[:, 'ORB'] + players_statistics[i].loc[:, 'DRB']
    players_statistics[i].loc[:, 'FG%'] = players_statistics[i].loc[:, 'PTS'] / 2 / players_statistics[i].loc[:, 'FGA']
    players_statistics[i].loc[:, 'PTS/G'] = players_statistics[i].loc[:, 'PTS'] / (j+1)
    players_statistics[i].loc[:, 'TRB/G'] = players_statistics[i].loc[:, 'TRB'] / (j + 1)
    players_statistics[i].loc[:, 'AST/G'] = players_statistics[i].loc[:, 'AST'] / (j + 1)

    # players_statistics[i].loc[:, 'Team'] = i
    players_statistics[i] = players_statistics[i][cols]
    decimals = 2
    for c in ['PTS/G', 'TRB/G', 'AST/G']:
        players_statistics[i][c] = players_statistics[i][c].apply(lambda x: round(x, decimals))

#TODO: Make a function
players_standings = pd.concat(players_statistics, axis=0)
players_standings = players_standings.sort_values(by=['PTS', 'FG%', 'TRB', 'AST'], ascending=False)


#TODO: Make a function
results.to_csv('E:\\Projects\\Github\\bracket_generator\\database\\Test/Results.csv', index=False)

#TODO: Check if this test is needed
for i in teams.index:
    tmp = players_statistics[i].sum()
    print('Team ' + i + ' AS: ' + str(round(tmp['AST'] / 11, 1)) + ' RB_OFF: ' + str(
        round(tmp['ORB'] / 11, 1)) + ' RB_DEF: ' + str(round(tmp['DRB'] / 11, 1)))
