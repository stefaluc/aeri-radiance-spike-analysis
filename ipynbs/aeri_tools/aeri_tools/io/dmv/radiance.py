from aeri_tools.io.dmv.util import to_dmv
from aeri_tools.io.util import get_times_from_hours, get_dates_from_yymmdd, get_scenes_from_sceneMirrorPositions, \
    get_datetime_index

__author__ = 'cphillips'

import numpy as np
import pandas as pd
from datetime import datetime

import os
from glob import glob

import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)


def get_radiance_from_rnc(path_or_dmv, column=1):
    """
    Get a dataframe containing the mean radiance from an rnc
    :param path_or_dmv:
    :param column:
    :return dataframe:
    """
    with to_dmv(path_or_dmv) as dmv:
        hours,dates,scene = dmv.get_meta_matrix(names=["Time","dateYYMMDD","sceneMirrorPosition"]).transpose()
        times = get_times_from_hours(hours)
        dates = get_dates_from_yymmdd(dates)
        scene = get_scenes_from_sceneMirrorPositions(scene)
        datetime_index = get_datetime_index(dates, times)
        df =  pd.DataFrame(dmv.get_dep_matrix(column),
                     columns=dmv.get_ind_values(1,column),
                     index=[datetime_index,scene]
        )
        df.index.set_names(["time","scene"],inplace=True)
        return df


def get_complex_radiance_from_rnc(path_or_dmv):
    real = get_radiance_from_rnc(path_or_dmv, column=1)
    imag = get_radiance_from_rnc(path_or_dmv, column=2)

    return real + 1j * imag


def get_complex_spectrum_from_rnc(base_path, date=None, **kwargs):
    real = get_spectrum_from_rnc(base_path, date=date, column=1, **kwargs)
    imag = get_spectrum_from_rnc(base_path, date=date, column=2, **kwargs)

    return real + 1j * imag


def get_spectrum_from_rnc(base_path, date=None, column=1, ch1_name='*C1.RNC', ch2_name='*C2.RNC'):
    """
    Get full spectrum from both channels
    :param base_path:
    :param date:
    :return Dataframe of full spectrum for all records:
    """
    if not os.path.isdir(base_path):
        base_path = os.path.dirname()

    if date:
        if isinstance(date,datetime):
            date = date.strftime('%y%m%c')
        ch1_name = date+'C1.RNC'
        ch2_name = date+'C2.RNC'

    ch1 = glob(os.path.join(base_path,ch1_name))
    ch2 = glob(os.path.join(base_path,ch2_name))

    if len(ch1) > 1 or len(ch2) > 1:
        raise EnvironmentError("Too many files")
    elif len(ch1) == 0 or len(ch2) == 0:
        raise EnvironmentError("No files")
    else:
        ch1,ch2 = ch1[0],ch2[0]

    return get_radiance_from_rnc(ch1, column=column).join(get_radiance_from_rnc(ch2, column=column)).T.sort_index().T

def zero_pad_spectrum(spectrum):
    values = spectrum.columns.values
    differences = (values[1:] - values[:-1])
    mean_diff = differences.mean()

    if differences.max() - mean_diff > 1 or differences.min() - mean_diff < -1:
        raise ValueError("Columns are not regular")

    pad = np.arange(0,spectrum.columns[0],mean_diff)

    padding_data = np.zeros((spectrum.shape[0],pad.size))

    padding = pd.DataFrame(padding_data,columns=pad,index=spectrum.index)

    return pd.concat([padding, spectrum], axis=1)
