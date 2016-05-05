__author__ = 'cphillips'

from . import pandas_read_spectral_cal
from ..util import as_netcdf
import pandas as pd


def open_store(path, mode='a'):
    return pd.HDFStore(path, mode=mode)


def add_cdf_to_store(path_or_cdf, store):
    with as_netcdf(path_or_cdf) as cdf:
        scalars = pandas_read_spectral_cal.get_zero_dimensional_frame(cdf)
        aeri = pandas_read_spectral_cal.get_aeri_data_frame(cdf)
        lblrtm = pandas_read_spectral_cal.get_lblrtm_data_frame(cdf)
        sonde = pandas_read_spectral_cal.get_sonde_frame(cdf)
        sonde.index = pd.MultiIndex.from_product(((aeri.index[0],), sonde.index))
        store.append('scalars', scalars)
        store.append('aeri/rad_730_740', aeri.ix[:, 730.:740.])
        store.append('lblrtm/rad_730_740', lblrtm.ix[:, 730.:740.])
        store.append('sonde', sonde)
