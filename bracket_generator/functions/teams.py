import pandas as pd
import random

class Team:
    def __init__(team, name, offence, defence, division=None, conference=None, league=None):
        team.name = name
        team.offence = offence
        team.defence = defence
        team.division = division
        team.conference = conference
        team.league = league
        team.W = team.L = team.pts_for = team.pts_against = 0

# t1 = Team('test', 7, -2)

league_size = 4
team_names = ['A', 'B', 'C']
teams = []
for _ in team_names:
    teams.append(Team(str(_),
                      int(input('Team '+str(_)+"'s offence level: ")),
                      int(input('Team '+str(_)+"'s defence level: ")),
                      input('Team '+str(_)+'s division :')))



for team in teams:
    print(team.name, team.offence, team.defence, team.points, team.division, team.conference)