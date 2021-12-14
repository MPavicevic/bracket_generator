import pandas as pd


def create_balanced_round_robin(players, order=1):
    """ Create a schedule for the players in the list and return it"""
    s = []
    if len(players) % 2 == 1:
        players = players + [None]
    # manipulate map (array of indexes for list) instead of list itself
    # this takes advantage of even/odd indexes to determine home vs. away
    n = len(players)
    mapping = list(range(n))
    mid = n // 2
    for i in range(n - 1):
        l1 = mapping[:mid]
        l2 = mapping[mid:]
        l2.reverse()
        rnd = []
        for j in range(mid):
            t1 = players[l1[j]]
            t2 = players[l2[j]]
            if j == 0 and i % 2 == 1:
                # flip the first match only, every other round
                # (this is because the first match always involves the last player in the list)
                # round.append([t2, t1])
                if order == 1:
                    rnd += [str(t2) + ' .vs ' + str(t1)]
                else:
                    rnd += [str(t1) + ' .vs ' + str(t2)]
            else:
                # round.append([t1, t2])
                if order == 1:
                    rnd += [str(t1) + ' .vs ' + str(t2)]
                else:
                    rnd += [str(t2) + ' .vs ' + str(t1)]
        s.append(rnd)
        # rotate list by n/2, leaving last element at the end
        mapping = mapping[mid:-1] + mapping[:mid] + mapping[-1:]
    return s


def shift(seq, n=0):
    a = n % len(seq)
    return seq[-a:] + seq[:-a]


def create_balanced_round_robin_2_lists(players1, players2):
    """ Create a schedule for the players in the list and return it"""
    s = []
    # manipulate map (array of indexes for list) instead of list itself
    # this takes advantage of even/odd indexes to determine home vs. away
    n = len(players1)
    for i in range(n):
        rnd = []
        for j in range(n):
            t1 = players1[j]
            t2 = players2[j]
            if i % 2 == 1:
                # flip the first match only, every other round
                # (this is because the first match always involves the last player in the list)
                # round.append([t2, t1])
                rnd += [str(t2) + ' .vs ' + str(t1)]
            else:
                # round.append([t1, t2])
                rnd += [str(t1) + ' .vs ' + str(t2)]
        s.append(rnd)
        # rotate list by n/2, leaving last element at the end
        players2 = shift(players2, 1)
    return s


def df_from_list(teams, order=1):
    schedule = create_balanced_round_robin(teams, order=order)
    return pd.DataFrame(schedule)


def merge_dfs(df1, df2):
    df = pd.merge(df1, df2, left_index=True, right_index=True)
    return df.T.reset_index(drop=True).T


def concat_dfs(df1, df2):
    return pd.concat([df1, df2])


def get_division_fixtures(divisions, order=1):
    schedule = pd.DataFrame()
    i = 0
    for teams in divisions:
        df2 = df_from_list(teams, order=order)
        i = i + 1
        if i == 1:
            schedule = df2
        else:
            schedule = merge_dfs(schedule, df2)
    return schedule


def get_conference_fixtures(conferences, order=1):
    schedule = pd.DataFrame()
    i = 0
    for conf in conferences:
        if order == 1:
            df = pd.DataFrame(create_balanced_round_robin_2_lists(conf[0], conf[1]))
        else:
            df = pd.DataFrame(create_balanced_round_robin_2_lists(conf[1], conf[0]))
        i = i + 1
        if i == 1:
            schedule = df
        else:
            schedule = merge_dfs(schedule, df)
    return schedule


def create_division_league_fixtures(divisions, conferences, order=1):
    if order == 1:
        ds_1 = get_division_fixtures(divisions=divisions, order=1)
        cs_1 = get_conference_fixtures(conferences, order=1)
        ds_2 = get_division_fixtures(divisions=divisions, order=2)
    else:
        ds_1 = get_division_fixtures(divisions=divisions, order=1)
        cs_1 = get_conference_fixtures(conferences, order=2)
        ds_2 = get_division_fixtures(divisions=divisions, order=2)
    schedule = concat_dfs(ds_1, cs_1)
    schedule = concat_dfs(schedule, ds_2)
    return schedule.reset_index(drop=True)


def create_fixtures(divisions, conferences, league):
    round1 = create_division_league_fixtures(divisions, conferences, order=1)
    round2 = pd.DataFrame(create_balanced_round_robin_2_lists(league[0], league[1]))
    schedule = concat_dfs(round1, round2)
    round3 = create_division_league_fixtures(divisions, conferences, order=2)
    schedule = concat_dfs(schedule, round3)
    return schedule.reset_index(drop=True)
