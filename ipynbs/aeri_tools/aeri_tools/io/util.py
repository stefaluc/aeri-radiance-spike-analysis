import numpy as np
import pandas as pd
from contextlib import contextmanager

__author__ = 'cphillips'


def get_times_from_hours(hours):
    times = pd.to_timedelta((hours * 3600000).astype(np.uint32), unit='ms')
    return times


def get_dates_from_yymmdd(dates):
    dates = pd.to_datetime(["{:06.0f}".format(x) for x in dates], format="%y%m%d", coerce=True)
    return dates


def get_scenes_from_sceneMirrorPositions(mirror_positions):
    positions = np.empty_like(mirror_positions, dtype=np.character)
    for i, x in enumerate(mirror_positions):
        try:
            if np.isnan(float(x)):
                positions[i] = '?'
            else:
                positions[i] = chr(int(float(x)))
        except ValueError:
            positions[i] = '?'
    return positions



def get_datetime_index(dates, times):
    datetime_index = pd.DatetimeIndex(pd.Series(dates) + times)
    return datetime_index

@contextmanager
def as_netcdf(path_or_netcdf):
    if isinstance(path_or_netcdf,basestring):
        from netCDF4 import Dataset
        fp = Dataset(path_or_netcdf)
        yield fp
        fp.close()
    else:
        yield path_or_netcdf