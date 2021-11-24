from datetime import datetime
from collections import defaultdict
import pandas as pd
import numpy as np


def calculate_match_points(team1, team2, score1, score2, points_win=2, points_draw=1, points_loss=0):
    if score1 == score2:
        return {team1: points_draw, team2: points_draw}
    elif score1 > score2:
        return {team1: points_win, team2: points_loss}
    else:
        return {team1: points_loss, team2: points_win}


class LeagueTable:
    def table(self, league, points_win=2, points_draw=1, points_loss=0):
        year = int(datetime.now().strftime('%Y'))
        # results = pd.read_csv('./data/' + league + '_' + str(year) + '.csv')
        results_import = pd.read_csv(
            'E:\\Projects\\Github\\bracket_generator\\data/' + league + '_' + str(year) + '.csv')

        print(f"Running {league} table generator for year {str(year)}")

        final_table = {}
        streak = {}
        for round in np.unique(results_import[['Round']].values):

            results = results_import.loc[results_import['Round'] <= round]
            final_table[round] = defaultdict(
                lambda: {'W': 0, 'L': 0, 'WIN%': 0.000, 'HOME': '0-0', 'ROAD': '0-0', 'OT': '0-0',
                         'OT_W': 0, 'OT_L': 0,
                         'CONF_W': 0, 'CONF_L': 0, 'CONF': '0-0',
                         'DIV_W': 0, 'DIV_L': 0, 'DIV': '0-0',
                         'PTS': 0, 'PA': 0, 'gd': 0, 'PTS/g': 0, 'PA/g': 0, '+/-/g': 0,
                         'points': 0, })

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

                    # Check overtime
                    over_time = results.loc[match, 'OT']

                    # Compute match outcome
                    match_outcome = calculate_match_points(team1, team2, score1, score2, points_win, points_draw,
                                                           points_loss)

                    # Assign win lose to home/away teams
                    win_home = final_table[round][team1]['W'] + match_outcome[team1] / points_win
                    loss_home = final_table[round][team1]['L'] + match_outcome[team2] / points_win
                    win_away = final_table[round][team2]['W'] + match_outcome[team2] / points_win
                    loss_away = final_table[round][team2]['L'] + match_outcome[team1] / points_win

                    # Calculation of overtime games
                    if over_time == 'Yes':
                        ot_win_home = final_table[round][team1]['OT_W'] + match_outcome[team1] / points_win
                        ot_loss_home = final_table[round][team1]['OT_L'] + match_outcome[team2] / points_win
                        ot_win_away = final_table[round][team2]['OT_W'] + match_outcome[team2] / points_win
                        ot_loss_away = final_table[round][team2]['OT_L'] + match_outcome[team1] / points_win
                    else:
                        ot_win_home = final_table[round][team1]['OT_W']
                        ot_loss_home = final_table[round][team1]['OT_L']
                        ot_win_away = final_table[round][team2]['OT_W']
                        ot_loss_away = final_table[round][team2]['OT_L']

                    # Scored/received points home team
                    pts_ft_home = final_table[round][team1]['PTS'] + results.loc[match, 'Home F/T Points']
                    pts_ft_away = final_table[round][team2]['PTS'] + results.loc[match, 'Away F/T Points']
                    pa_ft_home = final_table[round][team1]['PA'] + results.loc[match, 'Away F/T Points']
                    pa_ft_away = final_table[round][team2]['PA'] + results.loc[match, 'Home F/T Points']
                    pts_ft_home_g = pts_ft_home / (win_home + loss_home)
                    pts_ft_away_g = pts_ft_away / (win_away + loss_away)
                    pa_ft_home_g = pa_ft_home / (win_home + loss_home)
                    pa_ft_away_g = pa_ft_away / (win_away + loss_away)
                    # plus_minus_home_g = pts_ft_home_g - pa_ft_away_g
                    # plus_minus_away_g = pts_ft_away_g - pa_ft_home_g

                    # Conference and division games
                    if team1_conf == team2_conf:
                        if team1_div != team2_div:
                            # Conference games
                            conf_win_home = final_table[round][team1]['CONF_W'] + match_outcome[team1] / points_win
                            conf_loss_home = final_table[round][team1]['CONF_L'] + match_outcome[team2] / points_win
                            conf_win_away = final_table[round][team2]['CONF_W'] + match_outcome[team2] / points_win
                            conf_loss_away = final_table[round][team2]['CONF_L'] + match_outcome[team1] / points_win
                            # Division games
                            div_win_home = final_table[round][team1]['DIV_W']
                            div_loss_home = final_table[round][team1]['DIV_L']
                            div_win_away = final_table[round][team2]['DIV_W']
                            div_loss_away = final_table[round][team2]['DIV_L']
                        else:
                            # Conference games
                            conf_win_home = final_table[round][team1]['CONF_W']
                            conf_loss_home = final_table[round][team1]['CONF_L']
                            conf_win_away = final_table[round][team2]['CONF_W']
                            conf_loss_away = final_table[round][team2]['CONF_L']
                            # Division games
                            div_win_home = final_table[round][team1]['DIV_W'] + match_outcome[team1] / points_win
                            div_loss_home = final_table[round][team1]['DIV_L'] + match_outcome[team2] / points_win
                            div_win_away = final_table[round][team2]['DIV_W'] + match_outcome[team2] / points_win
                            div_loss_away = final_table[round][team2]['DIV_L'] + match_outcome[team1] / points_win

                    else:
                        # Conference games
                        conf_win_home = final_table[round][team1]['CONF_W']
                        conf_loss_home = final_table[round][team1]['CONF_L']
                        conf_win_away = final_table[round][team2]['CONF_W']
                        conf_loss_away = final_table[round][team2]['CONF_L']
                        # Division games
                        div_win_home = final_table[round][team1]['DIV_W']
                        div_loss_home = final_table[round][team1]['DIV_L']
                        div_win_away = final_table[round][team2]['DIV_W']
                        div_loss_away = final_table[round][team2]['DIV_L']

                    # Update final table for home team
                    final_table[round][team1] = {
                        'name': team1,
                        'W': int(win_home),
                        'L': int(loss_home),
                        'WIN%': "{:.3f}".format(0) if win_home == 0 else "{:.3f}".format(
                            (win_home / (win_home + loss_home))),
                        'HOME': str(int(win_home)) + '-' + str(int(loss_home)),
                        'ROAD': final_table[round][team1]['ROAD'],
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
                        'gd': final_table[round][team1]['gd'] + (score1 - score2),
                        'points': final_table[round][team1]['points'] + match_outcome[team1],
                        'PTS/g': "{:.1f}".format(pts_ft_home_g),
                        'PA/g': "{:.1f}".format(pa_ft_home_g)
                    }
                    # Update final table of away team
                    final_table[round][team2] = {
                        'name': team2,
                        'W': int(win_away),
                        'L': int(loss_away),
                        'WIN%': "{:.3f}".format(0) if win_away == 0 else "{:.3f}".format(
                            (win_away / (win_away + loss_away))),
                        'HOME': final_table[round][team2]['HOME'],
                        'ROAD': str(int(win_away)) + '-' + str(int(loss_away)),
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
                        'gd': final_table[round][team2]['gd'] + (score2 - score1),
                        'points': final_table[round][team2]['points'] + match_outcome[team2],
                        'PTS/g': "{:.1f}".format(pts_ft_away_g),
                        'PA/g': "{:.1f}".format(pa_ft_away_g)
                    }

            final_table[round] = sorted(final_table[round].values(), key=lambda x: (-x['points'], -x['gd']))
            tmp = pd.DataFrame(final_table[round])
            tmp.loc[:, 'GB'] = (tmp.at[0, 'W'] - tmp.loc[1:, 'W'] + tmp.loc[1:, 'L'] - tmp.at[0, 'L']) / 2
            tmp.fillna(0, inplace=True)

            streak[round] = tmp
            final_table[round] = tmp.to_dict('records')
            # final_table[round].loc[]
        df = pd.concat(streak.values(), keys=streak.keys())
        streak = {}
        for team in np.unique(df[['name']].values):
            streak[team]=df.loc[df['name'] == team, :]
            w = int(streak[team].iloc[0,1].copy())
            l = int(streak[team].iloc[0,2].copy())
            streak[team].loc[:, 'Wins'] = streak[team]['W'] - streak[team]['W'].shift(1)
            streak[team].loc[:, 'Wins'].fillna(w,inplace=True)
            streak[team].loc[:, 'Losses'] = streak[team]['L'] - streak[team]['L'].shift(1)
            streak[team].loc[:, 'Losses'].fillna(l,inplace=True)
            # streak[team].loc[:,'STREAK']=streak[team].loc[:,'W']-streak[team].loc[:,'L']
        return final_table


if __name__ == "__main__":
    print(LeagueTable.table(LeagueTable, 'Test2_League'))
