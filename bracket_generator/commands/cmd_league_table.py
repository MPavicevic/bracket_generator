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
@click.option('-l', '--league', type=str, help='The leage code to view', default='Test2_League')
@click.option('-r', '--round', type=int, help='Round to view', default=1)
@click.pass_context
def table(ctx, league, round):
    """View a table"""
    table = ctx.obj.league_table.table(league)
    max_round=max(k for k, v in table.items())
    if round > max_round:
        print('Selected round doesnt exist!!! Results are displayed for the last recorded round: ' + str(max_round))
        table = table[max_round]
    else:
        table = table[round]
    pd.DataFrame(table)

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

    click.echo(f"{lbl_rank} {lbl_name} {lbl_w} {lbl_l} {lbl_win_prc} {lbl_gb} {lbl_conf} {lbl_div} {lbl_home} {lbl_road} {lbl_ot} {lbl_pts} {lbl_pa} {lbl_stats} {lbl_pts_g} {lbl_pa_g} {lbl_points}")
    for i, team in enumerate(table):
        rank = '{:>6}'.format(f"{i + 1}{pos_number(i+1)}:")
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
        click.echo(f"{rank} {name} {win} {loss} {win_prc} {gb} {conf} {div} {home} {road} {ot} {pts} {pa} {stats} {pts_g} {pa_g} {points}")


def pos_number(pos):
    return {1: "st", 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd'}.get(pos, 'th')
