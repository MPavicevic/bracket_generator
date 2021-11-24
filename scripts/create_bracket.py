import pandas as pd

import bracket_generator as bg

# Define divisions
divisionA = ["A1", "A2", "A3", "A4"]
divisionB = ["B1", "B2", "B3", "B4"]
divisionC = ["C1", "C2", "C3", "C4"]
divisionD = ["D1", "D2", "D3", "D4"]


divisions = [divisionA, divisionB, divisionC, divisionD]
conferences = [[divisionA, divisionB], [divisionC, divisionD]]
league = [divisionA + divisionB, divisionC + divisionD]
schedule = bg.create_fixtures(divisions, conferences, league)

from sympy.utilities.iterables import multiset_combinations

numbers = [1,2,3,4,5,6,5,4,3,2,1]
sums = [ ]
items = []
for n in range(2,1+len(numbers)):
     for item in multiset_combinations([1,2,3,4,5,6,5,4,3,2,1],n):
         items.append(item)
         added = sum(item)
         if not added in sums:
             sums.append(added)

sums.sort()

def subset_sum(numbers, target, partial=[]):
    s = sum(partial)
    # Check if the partial sum equals the target
    if s==target:
        print("sum(%s)=%s" % (partial, target))
        return partial
    if s>=target:
        return

    for i in range(len(numbers)):
        n=numbers[i]
        remaining=numbers[i + 1:]
        subset_sum(remaining, target, partial + [n])

# subset_sum(numbers, 4)

from itertools import combinations

def SumTheList(thelist, target):
    arr=[]
    p=[]
    if len(thelist)>0:
        for r in range(0,len(thelist)+1):
            arr += list(combinations(thelist, r))

        for item in arr:
            if sum(item) == target:
                p.append(item)

    p = list(set(p))
    q = [sorted(item) for item in p]
    q = list(set(map(tuple, q)))
    q.sort(key=lambda x:len(x))
    return q

b = []
for i in range(1, 37, 1):
    b.append(SumTheList(numbers, i))

combinations = pd.DataFrame(b)
combinations.index += 1
combinations.columns +=1

from itertools import combinations
import pandas as pd

a = pd.DataFrame(list(combinations('ABCDEFGHIJ', 2)))

a.to_csv('League.csv')

a = pd.read_csv('../data/Test_League_2021.csv')

for match in a.index:
    print(a.loc[match, 'Home F/T Points'])