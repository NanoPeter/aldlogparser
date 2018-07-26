from dateutil.parser import parse as dateparse
import pandas as pd
from datetime import datetime

import sys

def read_recipe_log_file(file_path):
    dates = []
    texts = []

    with open(file_path, 'r') as fil:
        for line in fil:

            date_string, rest = line.split(' ', maxsplit=1)

            date = dateparse(date_string)
            rest = rest[1:].strip()

            dates.append(date)
            texts.append(rest)

    return pd.DataFrame({'Datetime': dates, 'Text': texts})

def get_cycle_mapping(dataframe):
    cycle = 0
    mapping = []
    for index, row in dataframe.iterrows():
        if 'CYCLE' in row['Text']:
            cycle += 1
        mapping.append(cycle)
    return pd.Series(mapping, dtype="category")

def get_phases(group):
    starts = []
    ends = []
    phases = []
    cycles = []

    phase = 'None'


    for index, row in group[1].iterrows():
        text = row['Text'].lower()
        if phase == 'None':
            if 'open' in text and 'platinum' in text:
                phase = 'platinum'
                starts.append(row['Datetime'])
                cycles.append(group[0])
                phases.append(phase)
            elif 'open' in text and 'oxygen' in text:
                phase = 'oxygen'
                starts.append(row['Datetime'])
                cycles.append(group[0])
                phases.append(phase)
        elif phase == 'platinum':
            if 'close' in text and 'platinum' in text:
                phase = 'None'
                ends.append(row['Datetime'])
        elif phase == 'oxygen':
            if 'close' in text and 'oxygen' in text:
                phase = 'None'
                ends.append(row['Datetime'])

    df = pd.DataFrame({'start': starts, 'end': ends, 'phase': phases, 'cycle': cycles})
    return df

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('ERROR', 'wrong number of arguments')
        exit(0)

    file_name = sys.argv[1]

    df = read_recipe_log_file(file_name)
    mapping = get_cycle_mapping(df)
    groups = df.groupby(by=mapping)

    with open('{}.dat'.format(file_name), 'w') as fil:

        fil.write('#extracted from {}\n'.format(file_name))
        fil.write('cycle phase start end\n')

        for group in groups:
            phases = get_phases(group)
            for index, row in phases.iterrows():
                fil.write('{row[cycle]} {row[phase]} {row[start]} {row[end]}\n'.format(row=row))

    print('{}.dat written'.format(file_name))
