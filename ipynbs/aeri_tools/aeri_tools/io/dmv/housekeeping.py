__author__ = 'cphillips'

from ..util import get_dates_from_yymmdd,get_times_from_hours,get_datetime_index
from .util import  to_dmv
import pandas as pd

import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)


def get_all_housekeeping(path_or_dmv):
    """
    Return a dataframe of all metadata present in a dmv file
    :param path_or_dmv: path to dmv file or dmv file
    :return DataFrame: datetime index, variable named columns
    """
    with to_dmv(path_or_dmv) as dmv:
        hours,dates = dmv.get_meta_matrix(names=["Time","dateYYMMDD"]).transpose()
        times = get_times_from_hours(hours)
        dates = get_dates_from_yymmdd(dates)
        datetime_index = get_datetime_index(dates,times)
        names = dmv.get_meta_descs()
        return pd.DataFrame(dmv.get_meta_matrix(names=names),index=datetime_index,columns=names, )


def get_mean_mirror_steps(housekeeping_df):
    pos_step = housekeeping_df.loc[:, ('sceneMirrorPosition', 'sceneMirrorMotorStep')].groupby(
        'sceneMirrorPosition').mean()
    for scene,position in pos_step.iterrows():
        yield (scene, position['sceneMirrorMotorStep'])


def get_sky_view_smpi(housekeeping_df):
    """
    Get all characters representing sky (zenith) scene views
    :param housekeeping_df: DataFrame of housekeeping data
    :return [char1,...]: List of characters
    """
    for scene,position in get_mean_mirror_steps(housekeeping_df):
        if -1 < (position - 180) < 1:
            yield chr(int(scene))



