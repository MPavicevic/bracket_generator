import click
import pandas as pd

from bracket_generator.functions import league_table


class Context:
    def __init__(self):
        self.league_table = league_table.LeagueTable()


@click.group()
@click.pass_context
def cli(ctx):
    """League table results"""
    ctx.obj = Context()


@cli.command()
@click.option('-l', '--league', type=str, help='The league code to view (name of the .csv file)',
              default='Test2_League_2021')
@click.option('-r', '--rnd', type=int, help='Round to view', default=1)
@click.option('-c', '--conference', type=str, help='Name of the conference to be displayed', default=None)
@click.option('-d', '--division', type=str, help='Name of the division to be displayed', default=None)
@click.pass_context
def table(ctx, league, rnd, conference, division):
    """View the table"""

    tbl, conf, divi = ctx.obj.league_table.table(league)
    max_round = max(k for k, v in tbl.items())
    if rnd > max_round:
        print('Selected round doesnt exist!!! Results are displayed for the last recorded round: ' + str(max_round))
        tbl = tbl[max_round]
    else:
        tbl = tbl[rnd]

    # Display headers
    headers()
    # Display team standings
    for i, team in enumerate(tbl):
        teams(i, team)

    # Display Conference standings
    display_table(conf, rnd, name=conference)

    # Display Division standings
    display_table(divi, rnd, name=division)


def display_table(data, rnd, name=None):
    # Display Conference standings
    if name is None:
        pass
    elif name == 'all':
        for c in data:
            print(f"League table displayed for: {c}:")
            headers()
            for i, team in enumerate(data[c][rnd]):
                teams(i, team)
    else:
        print(f"League table displayed for: {name}:")
        headers()
        for i, team in enumerate(data[name][rnd]):
            teams(i, team)


def pos_number(pos):
    return {1: "st", 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd'}.get(pos, 'th')


def headers():
    lbl_rank = f"Rank".center(6)
    lbl_name = f"Team Name".center(20)
    lbl_w = f"W".center(3)
    lbl_l = f"L".center(3)
    lbl_win_prc = f"WIN%".center(6)
    lbl_home = f"HOME".center(5)
    lbl_road = f"ROAD".center(5)
    lbl_ot = f"OT".center(5)
    lbl_pts = f"PTS".center(6)
    lbl_pa = f"PA".center(6)
    lbl_points = f"Points".center(6)
    lbl_stats = f"+/-".center(6)
    lbl_conf = f"CONF".center(5)
    lbl_div = f"DIV".center(5)
    lbl_pts_g = f"PTS/g".center(5)
    lbl_pa_g = f"PA/g".center(5)
    lbl_gb = f"GB".center(4)
    lbl_streak = f"STREAK".center(7)
    lbl_last5 = f"LAST 5".center(6)
    lbl_ahead_ht = f"AHEAD H/T".center(9)
    lbl_tied_ht = f"TIED H/T".center(9)
    lbl_behind_ht = f"BEHIND H/T".center(11)
    click.echo(
        f"{lbl_rank} {lbl_name} {lbl_w} {lbl_l} {lbl_win_prc} {lbl_gb} {lbl_conf} {lbl_div} {lbl_home} {lbl_road} {lbl_ot} {lbl_last5} {lbl_streak} {lbl_ahead_ht} {lbl_behind_ht} {lbl_tied_ht} {lbl_pts} {lbl_pa} {lbl_stats} {lbl_pts_g} {lbl_pa_g} {lbl_points}")


def teams(i, team):
    rank = '{:>6}'.format(f"{i + 1}{pos_number(i + 1)}:")
    name = '{:<20}'.format(f" {team['name']}")
    win = '{:>3}'.format(f"{team['W']}")
    loss = '{:>3}'.format(f"{team['L']}")
    win_prc = '{:>6}'.format(f"{team['WIN%']}")
    conf = '{:>5}'.format(f"{team['CONF']}")
    div = '{:>5}'.format(f"{team['DIV']}")
    home = '{:>5}'.format(f"{team['HOME']}")
    road = '{:>5}'.format(f"{team['ROAD']}")
    ot = '{:>5}'.format(f"{team['OT']}")
    pts = '{:>6}'.format(f"{team['PTS']}")
    pa = '{:>6}'.format(f"{team['PA']}")
    stats = '{:>6}'.format(f"{team['gd']}")
    pts_g = '{:>5}'.format(f"{team['PTS/g']}")
    pa_g = '{:>5}'.format(f"{team['PA/g']}")
    points = f"{team['points']}".center(6)
    gb = f"{team['GB']}".center(5)
    streak = '{:>6}'.format(f"{team['STREAK']}")
    last5 = '{:>6}'.format(f"{team['LAST 5']}")
    ahead_ht = '{:>9}'.format(f"{team['AHEAD HALF']}")
    behind_ht = '{:>11}'.format(f"{team['BEHIND HALF']}")
    tied_ht = '{:>9}'.format(f"{team['TIED HALF']}")

    click.echo(
        f"{rank} {name} {win} {loss} {win_prc} {gb} {conf} {div} {home} {road} {ot} {last5} {streak} {ahead_ht} {behind_ht} {tied_ht} {pts} {pa} {stats} {pts_g} {pa_g} {points}")
