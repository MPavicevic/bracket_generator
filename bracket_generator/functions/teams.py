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


def match_results(home_team, away_team, home_rolls, away_rolls, home_offence, home_defense, away_offence, away_defence, home_lti, away_lti):
    home_modifier = home_offence + away_defence + home_lti + 2
    away_modifier = away_offence + home_defense + away_lti - 2
    return {home_team: team_results(home_modifier, home_rolls), away_team: team_results(away_modifier, away_rolls)}


def round_results(matches, LTI_df):
    results = {}
    for match in matches:
        results[str(match)] = match_results(match[0], match[1], team_rolls(), team_rolls(),
                                            teams.loc[match[0], 'offense'], teams.loc[match[0], 'defence'],
                                            teams.loc[match[1], 'offense'], teams.loc[match[1], 'defence'],
                                            LTI_df.loc[teams.loc[match[0], 'LTI'], teams.loc[match[1], 'LTI']],
                                            LTI_df.loc[teams.loc[match[1], 'LTI'], teams.loc[match[0], 'LTI']])
    return results


leagues = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Leagues.csv', index_col=0)
conferences = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Conferences.csv', index_col=0)
divisions = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Divisions.csv', index_col=0)
teams = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Teams.csv', index_col=0)
schedule = pd.read_csv('E:\\Projects\\Github\\bracket_generator\\database/Test/Schedule.csv', index_col=0)

matches = {}
results = {}
for i in schedule.index:
    matches[i] = []
    results[i] = {}
    for j in schedule.columns:
        results[i][int(j)] = {}
        temp = iter(schedule.loc[i, j].split(" .vs "))
        res = [(ele, next(temp)) for ele in temp]
        matches[i].append(res)
        results[i][int(j)] = round_results(matches[i][int(j)], LTI_df)



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
