import pandas as pd
import re

__author__ = 'cphillips'


def get_labels(current_file):
    with open(current_file) as fd:
        labels = [re.match('#label [0-9]{1,2} (\w+)', line).group(1) for line in fd if
                  re.match('#label [0-9]{1,2} (\w+)', line)]
    return labels


def get_data(current_file):
    labels = get_labels(current_file)
    results = pd.read_table(current_file, delimiter='[\s]+', comment='#', header=None, names=labels, engine='python')
    try:
        date_string = re.search('([0-9]{6,8})',current_file).group(0)
    except AttributeError:
        date_string = None
    if date_string:
        date = pd.to_datetime(date_string)
    else:
        date = pd.to_datetime(results.DayOfYear,unit='d')
    times = pd.to_datetime(results.Hour,unit='h')-pd.to_datetime(0,unit='h')+date
    results.set_index(pd.DatetimeIndex(times),inplace=True)
    return results


