from datetime import datetime
from collections import defaultdict
import pandas as pd
import numpy as np


def get_match_points(team1, team2, score1, score2, points_win=2, points_draw=1, points_loss=0):
    """
    Compute home and away team points obtained in this match

    :param team1:       Home team
    :param team2:       Away team
    :param score1:      Home team points scored
    :param score2:      Away team points scored
    :param points_win:  Points awarded for a win
    :param points_draw: Points awarded for a draw
    :param points_loss: Points awarded for a loss
    :return:            Home and Away team points
    """
    if score1 == score2:
        return {team1: points_draw, team2: points_draw}
    elif score1 > score2:
        return {team1: points_win, team2: points_loss}
    else:
        return {team1: points_loss, team2: points_win}


def update_match_outcome(final_table, rnd, team1, team2, match_outcome, points_win, prefix=''):
    """
    Update match outcomes
    :param final_table:     final table where all the information is stored
    :param rnd:             name of the round
    :param team1:           Home team
    :param team2:           Away team
    :param match_outcome:   Computed match outcome
    :param points_win:      Points assigned for a win
    :param prefix:          String for different types of match results i.e. OT_, AHEAD HALF...
    :return:                Win loss for home and away teams
    """
    win_home = final_table[rnd][team1][prefix + 'W'] + match_outcome[team1] / points_win
    loss_home = final_table[rnd][team1][prefix + 'L'] + match_outcome[team2] / points_win
    win_away = final_table[rnd][team2][prefix + 'W'] + match_outcome[team2] / points_win
    loss_away = final_table[rnd][team2][prefix + 'L'] + match_outcome[team1] / points_win
    return win_home, loss_home, win_away, loss_away


def dont_update_match_outcome(final_table, rnd, team1, team2, prefix=''):
    """
    Dont update the final league table, just use previous values instead

    :param final_table:     final table where all the information is stored
    :param rnd:             name of the round
    :param team1:           Home team
    :param team2:           Away team
    :param prefix:          String for different types of match results i.e. OT_, AHEAD HALF...
    :return:                Win loss for home and away teams
    """
    win_home = final_table[rnd][team1][prefix + 'W']
    loss_home = final_table[rnd][team1][prefix + 'L']
    win_away = final_table[rnd][team2][prefix + 'W']
    loss_away = final_table[rnd][team2][prefix + 'L']
    return win_home, loss_home, win_away, loss_away


class LeagueTable:
    def table(self, league, points_win=2, points_draw=1, points_loss=0):
        """
        Function for populating the final league table

        :param league:          Name of the league to be loaded
        :param points_win:      Points for wining a game
        :param points_draw:     Points for drawing a game
        :param points_loss:     Points for loosing a game
        :return:                Updated final league table
        """

        # results_import = pd.read_csv('./data/' + league + '.csv')
        results_import = pd.read_csv(
            'E:\\Projects\\Github\\bracket_generator\\database\\' + league + '/Results.csv')
        teams_import = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database\\' + league + '/Teams.csv')

        for t in teams_import.loc[:, 'id']:
            results_import.loc[results_import['Home Team'] == t, 'Home Team Conference'] = \
                list(teams_import.loc[teams_import['id'] == t, 'ConferenceId'])[0]
            results_import.loc[results_import['Away Team'] == t, 'Away Team Conference'] = \
                list(teams_import.loc[teams_import['id'] == t, 'ConferenceId'])[0]
            results_import.loc[results_import['Home Team'] == t, 'Home Team Division'] = \
                list(teams_import.loc[teams_import['id'] == t, 'DivisionId'])[0]
            results_import.loc[results_import['Away Team'] == t, 'Away Team Division'] = \
                list(teams_import.loc[teams_import['id'] == t, 'DivisionId'])[0]
        print(f"Running {league} table generator")

        final_table = {}
        table_rounds = {}
        for rnd in np.unique(results_import[['Round']].values):

            results = results_import.loc[results_import['Round'] <= rnd]
            final_table[rnd] = defaultdict(
                lambda: {'W': 0, 'L': 0, 'WIN%': 0.000, 'HOME': '0-0', 'ROAD': '0-0', 'OT': '0-0',
                         'OT_W': 0, 'OT_L': 0,
                         'CONF_W': 0, 'CONF_L': 0, 'CONF': '0-0',
                         'DIV_W': 0, 'DIV_L': 0, 'DIV': '0-0',
                         'PTS': 0, 'PA': 0, 'gd': 0, 'PTS/g': 0, 'PA/g': 0, '+/-/g': 0,
                         'points': 0,
                         'AHEAD HALF': '0-0', 'BEHIND HALF': '0-0', 'TIED HALF': '0-0',
                         'AHEAD_HT_W': 0, 'AHEAD_HT_L': 0,
                         'BEHIND_HT_W': 0, 'BEHIND_HT_L': 0,
                         'TIED_HT_W': 0, 'TIED_HT_L': 0
                         })

            for match in results.index:
                if (results.loc[match, 'Home F/T Points']) and (results.loc[match, 'Away F/T Points']):
                    # Identify teams playing and conferences/divisions they belong to
                    team1 = results.loc[match, 'Home Team']
                    team2 = results.loc[match, 'Away Team']
                    team1_conf = results.loc[match, 'Home Team Conference']
                    team2_conf = results.loc[match, 'Away Team Conference']
                    team1_div = results.loc[match, 'Home Team Division']
                    team2_div = results.loc[match, 'Away Team Division']

                    # Identify scores
                    score1 = results.loc[match, 'Home F/T Points']
                    score2 = results.loc[match, 'Away F/T Points']
                    score1_ht = results.loc[match, 'Home H/T Points']
                    score2_ht = results.loc[match, 'Away H/T Points']

                    # Check overtime
                    over_time = results.loc[match, 'OT']

                    # Compute match outcome
                    match_outcome = get_match_points(team1, team2, score1, score2, points_win, points_draw, points_loss)

                    # Assign win lose to home/away teams
                    win_home, loss_home, win_away, loss_away = update_match_outcome(
                        final_table, rnd, team1, team2, match_outcome, points_win)

                    # Calculation of overtime games
                    if over_time == 'Yes':
                        ot_win_home, ot_loss_home, ot_win_away, ot_loss_away = update_match_outcome(
                            final_table, rnd, team1, team2, match_outcome, points_win, prefix='OT_')
                    else:
                        ot_win_home, ot_loss_home, ot_win_away, ot_loss_away = dont_update_match_outcome(
                            final_table, rnd, team1, team2, prefix='OT_')

                    # Calculation of wins/losses based on the half time results
                    if score1_ht == score2_ht:
                        tied_ht_w_home, tied_ht_l_home, tied_ht_w_away, tied_ht_l_away = update_match_outcome(
                            final_table, rnd, team1, team2, match_outcome, points_win, prefix='TIED_HT_')
                        ahead_ht_w_home, ahead_ht_l_home, ahead_ht_w_away, ahead_ht_l_away = dont_update_match_outcome(
                            final_table, rnd, team1, team2, prefix='AHEAD_HT_')
                        behind_ht_w_home, behind_ht_l_home, behind_ht_w_away, behind_ht_l_away = dont_update_match_outcome(
                            final_table, rnd, team1, team2, prefix='BEHIND_HT_')
                    elif score1_ht > score2_ht:
                        tied_ht_w_home, tied_ht_l_home, tied_ht_w_away, tied_ht_l_away = dont_update_match_outcome(
                            final_table, rnd, team1, team2, prefix='TIED_HT_')
                        ahead_ht_w_home, ahead_ht_l_home, ahead_ht_w_away, ahead_ht_l_away = update_match_outcome(
                            final_table, rnd, team1, team2, match_outcome, points_win, prefix='AHEAD_HT_')
                        behind_ht_w_home, behind_ht_l_home, behind_ht_w_away, behind_ht_l_away = dont_update_match_outcome(
                            final_table, rnd, team1, team2, prefix='BEHIND_HT_')
                    else:
                        tied_ht_w_home, tied_ht_l_home, tied_ht_w_away, tied_ht_l_away = dont_update_match_outcome(
                            final_table, rnd, team1, team2, prefix='TIED_HT_')
                        ahead_ht_w_home, ahead_ht_l_home, ahead_ht_w_away, ahead_ht_l_away = dont_update_match_outcome(
                            final_table, rnd, team1, team2, prefix='AHEAD_HT_')
                        behind_ht_w_home, behind_ht_l_home, behind_ht_w_away, behind_ht_l_away = update_match_outcome(
                            final_table, rnd, team1, team2, match_outcome, points_win, prefix='BEHIND_HT_')

                    # Scored/received points home team
                    pts_ft_home = final_table[rnd][team1]['PTS'] + results.loc[match, 'Home F/T Points']
                    pts_ft_away = final_table[rnd][team2]['PTS'] + results.loc[match, 'Away F/T Points']
                    pa_ft_home = final_table[rnd][team1]['PA'] + results.loc[match, 'Away F/T Points']
                    pa_ft_away = final_table[rnd][team2]['PA'] + results.loc[match, 'Home F/T Points']
                    pts_ft_home_g = pts_ft_home / (win_home + loss_home)
                    pts_ft_away_g = pts_ft_away / (win_away + loss_away)
                    pa_ft_home_g = pa_ft_home / (win_home + loss_home)
                    pa_ft_away_g = pa_ft_away / (win_away + loss_away)

                    # Conference and division games
                    if team1_conf == team2_conf:
                        if team1_div != team2_div:
                            # Conference games
                            conf_win_home, conf_loss_home, conf_win_away, conf_loss_away = update_match_outcome(
                                final_table, rnd, team1, team2, match_outcome, points_win, prefix='CONF_')
                            # Division games
                            div_win_home, div_loss_home, div_win_away, div_loss_away = dont_update_match_outcome(
                                final_table, rnd, team1, team2, prefix='DIV_')
                        else:
                            # Conference games
                            conf_win_home, conf_loss_home, conf_win_away, conf_loss_away = dont_update_match_outcome(
                                final_table, rnd, team1, team2, prefix='CONF_')
                            # Division games
                            div_win_home, div_loss_home, div_win_away, div_loss_away = update_match_outcome(
                                final_table, rnd, team1, team2, match_outcome, points_win, prefix='DIV_')

                    else:
                        # Conference games
                        conf_win_home, conf_loss_home, conf_win_away, conf_loss_away = dont_update_match_outcome(
                            final_table, rnd, team1, team2, prefix='CONF_')
                        # Division games
                        div_win_home, div_loss_home, div_win_away, div_loss_away = dont_update_match_outcome(
                            final_table, rnd, team1, team2, prefix='DIV_')

                    # Update final table for home team
                    final_table[rnd][team1] = {
                        'name': team1,
                        'W': int(win_home),
                        'L': int(loss_home),
                        'WIN%': "{:.3f}".format(0) if win_home == 0 else "{:.3f}".format(
                            (win_home / (win_home + loss_home))),
                        'HOME': str(int(int(final_table[rnd][team1]['HOME'].split("-")[0]) +
                                        match_outcome[team1] / points_win)) + '-' +
                                str(int(int(final_table[rnd][team1]['HOME'].split("-")[1]) +
                                        match_outcome[team2] / points_win)),
                        'ROAD': final_table[rnd][team1]['ROAD'],
                        'OT_W': int(ot_win_home),
                        'OT_L': int(ot_loss_home),
                        'OT': str(int(ot_win_home)) + '-' + str(int(ot_loss_home)),
                        'CONF_W': int(conf_win_home),
                        'CONF_L': int(conf_loss_home),
                        'CONF': str(int(conf_win_home)) + '-' + str(int(conf_loss_home)),
                        'DIV_W': int(div_win_home),
                        'DIV_L': int(div_loss_home),
                        'DIV': str(int(div_win_home)) + '-' + str(int(div_loss_home)),
                        'PTS': pts_ft_home,
                        'PA': pa_ft_home,
                        'gd': final_table[rnd][team1]['gd'] + (score1 - score2),
                        'points': final_table[rnd][team1]['points'] + match_outcome[team1],
                        'PTS/g': "{:.1f}".format(pts_ft_home_g),
                        'PA/g': "{:.1f}".format(pa_ft_home_g),
                        'AHEAD_HT_W': int(ahead_ht_w_home),
                        'AHEAD_HT_L': int(ahead_ht_l_home),
                        'AHEAD HALF': str(int(ahead_ht_w_home)) + '-' + str(int(ahead_ht_l_home)),
                        'TIED_HT_W': int(tied_ht_w_home),
                        'TIED_HT_L': int(tied_ht_l_home),
                        'TIED HALF': str(int(tied_ht_w_home)) + '-' + str(int(tied_ht_l_home)),
                        'BEHIND_HT_W': int(behind_ht_w_home),
                        'BEHIND_HT_L': int(behind_ht_l_home),
                        'BEHIND HALF': str(int(behind_ht_w_home)) + '-' + str(int(behind_ht_l_home)),
                    }
                    # Update final table of away team
                    final_table[rnd][team2] = {
                        'name': team2,
                        'W': int(win_away),
                        'L': int(loss_away),
                        'WIN%': "{:.3f}".format(0) if win_away == 0 else "{:.3f}".format(
                            (win_away / (win_away + loss_away))),
                        'HOME': final_table[rnd][team2]['HOME'],
                        'ROAD': str(int(int(final_table[rnd][team2]['ROAD'].split("-")[0]) +
                                        match_outcome[team2] / points_win)) + '-' +
                                str(int(int(final_table[rnd][team2]['ROAD'].split("-")[1]) +
                                        match_outcome[team1] / points_win)),
                        'OT_W': int(ot_win_away),
                        'OT_L': int(ot_loss_away),
                        'OT': str(int(ot_win_away)) + '-' + str(int(ot_loss_away)),
                        'CONF_W': int(conf_win_away),
                        'CONF_L': int(conf_loss_away),
                        'CONF': str(int(conf_win_away)) + '-' + str(int(conf_loss_away)),
                        'DIV_W': int(div_win_away),
                        'DIV_L': int(div_loss_away),
                        'DIV': str(int(div_win_away)) + '-' + str(int(div_loss_away)),
                        'PTS': pts_ft_away,
                        'PA': pa_ft_away,
                        'gd': final_table[rnd][team2]['gd'] + (score2 - score1),
                        'points': final_table[rnd][team2]['points'] + match_outcome[team2],
                        'PTS/g': "{:.1f}".format(pts_ft_away_g),
                        'PA/g': "{:.1f}".format(pa_ft_away_g),
                        'AHEAD_HT_W': int(ahead_ht_w_away),
                        'AHEAD_HT_L': int(ahead_ht_l_away),
                        'AHEAD HALF': str(int(ahead_ht_w_away)) + '-' + str(int(ahead_ht_l_away)),
                        'TIED_HT_W': int(tied_ht_w_away),
                        'TIED_HT_L': int(tied_ht_l_away),
                        'TIED HALF': str(int(tied_ht_w_away)) + '-' + str(int(tied_ht_l_away)),
                        'BEHIND_HT_W': int(behind_ht_w_away),
                        'BEHIND_HT_L': int(behind_ht_l_away),
                        'BEHIND HALF': str(int(behind_ht_w_away)) + '-' + str(int(behind_ht_l_away))
                    }

            final_table[rnd] = sorted(final_table[rnd].values(), key=lambda x: (-x['points'], -x['gd']))
            tmp = pd.DataFrame(final_table[rnd])
            tmp.loc[:, 'GB'] = (tmp.at[0, 'W'] - tmp.loc[1:, 'W'] + tmp.loc[1:, 'L'] - tmp.at[0, 'L']) / 2
            tmp.fillna(0, inplace=True)

            table_rounds[rnd] = tmp
            # final_table[rnd] = tmp.to_dict('records')
            # final_table[rnd].loc[]
        df = pd.concat(table_rounds.values(), keys=table_rounds.keys())
        streak = {}
        for team in np.unique(df[['name']].values):
            streak[team] = df.loc[df['name'] == team, :].copy()
            w = int(streak[team].iloc[0, 1].copy())
            l = int(streak[team].iloc[0, 2].copy())
            streak[team].loc[:, 'Wins'] = streak[team]['W'] - streak[team]['W'].shift(1)
            streak[team].loc[:, 'Wins'].fillna(w, inplace=True)
            streak[team].loc[:, 'Losses'] = streak[team]['L'] - streak[team]['L'].shift(1)
            streak[team].loc[:, 'Losses'].fillna(l, inplace=True)
            a = streak[team].loc[:, 'Wins'] != 0
            b = streak[team].loc[:, 'Losses'] != 0
            streak[team].loc[:, 'Cum_Wins'] = a.cumsum() - a.cumsum().where(~a).ffill().fillna(0).astype(int)
            streak[team].loc[:, 'Cum_Losses'] = b.cumsum() - b.cumsum().where(~b).ffill().fillna(0).astype(int)
            streak[team].loc[:, 'STREAK_W'] = 'W' + streak[team].loc[streak[team]['Cum_Wins'] > 0]['Cum_Wins'].astype(
                str)
            streak[team].loc[:, 'STREAK_L'] = 'L' + streak[team].loc[streak[team]['Cum_Losses'] > 0][
                'Cum_Losses'].astype(str)
            streak[team].loc[:, 'STREAK'] = streak[team].loc[:, 'STREAK_W'].fillna(streak[team].loc[:, 'STREAK_L'])
            streak[team].loc[:, 'W_Lst5'] = streak[team].loc[:, 'Wins'].rolling(min_periods=1, window=5).sum()
            streak[team].loc[:, 'L_Lst5'] = streak[team].loc[:, 'Losses'].rolling(min_periods=1, window=5).sum()
            streak[team].loc[:, 'LAST 5'] = streak[team].loc[:, 'W_Lst5'].astype(int).astype(str) + '-' + \
                                            streak[team].loc[:, 'L_Lst5'].astype(int).astype(str)

        for rnd in np.unique(results_import[['Round']].values):
            for team in np.unique(df[['name']].values):
                table_rounds[rnd].loc[table_rounds[rnd]['name'] == team, 'STREAK'] = streak[team].loc[(rnd, 'STREAK')]
                table_rounds[rnd].loc[table_rounds[rnd]['name'] == team, 'LAST 5'] = streak[team].loc[(rnd, 'LAST 5')]

            final_table[rnd] = table_rounds[rnd].to_dict('records')

        conference_table = {}
        conference_standings = {}
        for conference in np.unique(teams_import[['ConferenceId']].values):
            conference_standings[conference] = {}
            conference_table[conference] = {}
            for rnd in np.unique(results_import[['Round']].values):
                conference_standings[conference][rnd] = table_rounds[rnd].loc[
                    table_rounds[rnd]['name'].isin(teams_import.loc[teams_import['ConferenceId'] == conference, 'id'])]
                conference_standings[conference][rnd].reset_index(drop=True, inplace=True)
                conference_standings[conference][rnd].loc[:, 'GB'] = (conference_standings[conference][rnd].at[0, 'W'] -
                                                                      conference_standings[conference][rnd].loc[1:, 'W'] +
                                                                      conference_standings[conference][rnd].loc[1:, 'L'] -
                                                                      conference_standings[conference][rnd].at[0, 'L']) / 2
                conference_standings[conference][rnd].loc[:, 'GB'] = conference_standings[conference][rnd].loc[:, 'GB'].fillna(0)
                conference_table[conference][rnd] = conference_standings[conference][rnd].to_dict('records')

        division_table = {}
        division_standings = {}
        for division in np.unique(teams_import[['DivisionId']].values):
            division_standings[division] = {}
            division_table[division] = {}
            for rnd in np.unique(results_import[['Round']].values):
                division_standings[division][rnd] = table_rounds[rnd].loc[
                    table_rounds[rnd]['name'].isin(teams_import.loc[teams_import['DivisionId'] == division, 'id'])]
                division_standings[division][rnd].reset_index(drop=True, inplace=True)
                division_standings[division][rnd].loc[:, 'GB'] = (division_standings[division][rnd].at[0, 'W'] -
                                                                  division_standings[division][rnd].loc[1:, 'W'] +
                                                                  division_standings[division][rnd].loc[1:, 'L'] -
                                                                  division_standings[division][rnd].at[0, 'L']) / 2
                division_standings[division][rnd].loc[:, 'GB'] = division_standings[division][rnd].loc[:, 'GB'].fillna(0)
                division_table[division][rnd] = division_standings[division][rnd].to_dict('records')

        return final_table, conference_table, division_table


if __name__ == "__main__":
    print(LeagueTable.table(LeagueTable, 'Test'))
