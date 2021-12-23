import pandas as pd
import glob
import bracket_generator as bg
import os

league_name = 'Test1'

# Define divisions
divisionA = ["A1", "A2", 'A3', 'A4']
divisionB = ["B1", "B2", 'B3', 'B4']
divisionC = ["C1", "C2", 'C3', 'C4']
divisionD = ["D1", "D2", 'D3', 'D4']

# divisionA = ["A1", "A2"]
# divisionB = ["B1", "B2"]
# divisionC = ["C1", "C2"]
# divisionD = ["D1", "D2"]

divisions = [divisionA, divisionB, divisionC, divisionD]
conferences = [[divisionA, divisionB], [divisionC, divisionD]]
league = [divisionA + divisionB, divisionC + divisionD]
schedule = bg.create_fixtures(divisions, conferences, league)


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


create_folder('../database/' + league_name)
schedule.to_csv('../database/' + league_name + '/Schedule.csv')

df = pd.DataFrame(index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                  columns=['HomeRoll1', 'HomeRoll2', 'AwayRoll1', 'AwayRoll2'])
create_folder('../database/' + league_name + '/Rolls')
for rnd in schedule.index:
    create_folder('../database/' + league_name + '/Rolls/Round_' + str(rnd))
    for game in schedule.columns:

        df.to_csv('../database/' + league_name + '/Rolls/Round_' + str(rnd) + '/' + schedule.loc[rnd, game] + '.csv')
        df.to_csv('../database/' + league_name + '/Rolls/Round_' + str(rnd) + '/' + schedule.loc[rnd, game] + '.csv')


## Load data
leagues = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/'+league_name+'/Leagues.csv', index_col=0)
conferences = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/'+league_name+'/Conferences.csv', index_col=0)
divisions = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/'+league_name+'/Divisions.csv', index_col=0)
teams = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/'+league_name+'/Teams.csv', index_col=0)
schedule = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/'+league_name+'/Schedule.csv', index_col=0)
players_df = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/'+league_name+'/Players.csv')
rolls = bg.load_team_rolls('E:\\Projects\\Github\\bracket_generator\\database/'+league_name+'/Rolls/')
# Process data
players = bg.assign_players(players_df, teams)
scoring_lookup = bg.assign_scoring_lookup(teams, players)
# Compute results and stats
results, detailed_results, players_detailed_statistics = bg.get_detailed_stats_and_results(schedule, rolls,
                                                                                           scoring_lookup,
                                                                                           players, teams,
                                                                                           import_results=False)
players_statistics = bg.analyse_player_stats(players_detailed_statistics, players)
players_standings = bg.compute_players_standings(players_statistics)


#TODO: Make a function
results.to_csv('E:\\Projects\\Github\\bracket_generator\\database\\'+league_name+'/Results.csv', index=False)
players_standings.to_csv('E:\\Projects\\Github\\bracket_generator\\database\\'+league_name+'/Players_Standings.csv', encoding='utf-8-sig')

# from sympy.utilities.iterables import multiset_combinations
#
# numbers = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
# sums = []
# items = []
# for n in range(2, 1 + len(numbers)):
#     for item in multiset_combinations([1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1], n):
#         items.append(item)
#         added = sum(item)
#         if not added in sums:
#             sums.append(added)
#
# sums.sort()
#
#
# def subset_sum(numbers, target, partial=[]):
#     s = sum(partial)
#     # Check if the partial sum equals the target
#     if s == target:
#         print("sum(%s)=%s" % (partial, target))
#         return partial
#     if s >= target:
#         return
#
#     for i in range(len(numbers)):
#         n = numbers[i]
#         remaining = numbers[i + 1:]
#         subset_sum(remaining, target, partial + [n])
#
#
# # subset_sum(numbers, 4)
#
# from itertools import combinations
#
#
# def SumTheList(thelist, target):
#     arr = []
#     p = []
#     if len(thelist) > 0:
#         for r in range(0, len(thelist) + 1):
#             arr += list(combinations(thelist, r))
#
#         for item in arr:
#             if sum(item) == target:
#                 p.append(item)
#
#     p = list(set(p))
#     q = [sorted(item) for item in p]
#     q = list(set(map(tuple, q)))
#     q.sort(key=lambda x: len(x))
#     return q
#
#
# b = []
# for i in range(1, 37, 1):
#     b.append(SumTheList(numbers, i))
#
# combinations = pd.DataFrame(b)
# combinations.index += 1
# combinations.columns += 1
#
# from itertools import combinations
# import pandas as pd
#
# a = pd.DataFrame(list(combinations('ABCDEFGHIJ', 2)))
#
# a.to_csv('League.csv')
#
# a = pd.read_csv('../data/Test_League_2021.csv')
#
# for match in a.index:
#     print(a.loc[match, 'Home F/T Points'])
