import pandas as pd
from datetime import datetime
import numpy
from glob import glob
import os
import logging
from multiprocessing import Pool
from ..util import as_netcdf

logging.basicConfig()
LOG = logging.getLogger(__name__)


def test_good(path_or_nc):
    """
    Args:
    path_or_nc: file path string or netCDF4 object

    Test a netCDF for good data
    """

    with as_netcdf(path_or_nc) as nc:
        isgood = not numpy.isnan(nc.variables['min_sw_rms'][:]).any()

    return isgood

def get_sonde_frame(path_or_nc):
    with as_netcdf(path_or_nc) as nc:
        sonde_rh = nc.variables['sonde_rh'][:]
        sonde_w = nc.variables['sonde_w'][:]
        sonde_alt = nc.variables['sonde_altitude'][:]
        sonde_pressure = nc.variables['sonde_pressure'][:]
        sonde_temperature = nc.variables['sonde_temperature'][:]
    df = pd.DataFrame({'rh':sonde_rh, 'w':sonde_w, 'altitude':sonde_alt, 'pressure':sonde_pressure, 'temperature':sonde_temperature})
    return df.set_index('pressure')

def get_lbl_lwrad(path_or_nc):
    with as_netcdf(path_or_nc) as nc:
        return nc.variables['lbl_lwrad_zf'][:]


def get_lwrad(path_or_nc):
    with as_netcdf(path_or_nc) as nc:
        return nc.variables['lwrad_mean_zf'][:]


def get_lwwn_zf(path_or_nc):
    with as_netcdf(path_or_nc) as nc:
        return nc.variables['lwwn_zf'][:]


def get_data_frame(path_or_nc):
    with as_netcdf(path_or_nc) as nc:
        lwrad = get_aeri_data_frame(nc)
        lbl_lwrad = get_lblrtm_data_frame(nc)
        return pd.concat([lwrad, lbl_lwrad], keys=['aeri', 'lblrtm'], axis=1)


def get_aeri_data_frame(path_or_nc):
    with as_netcdf(path_or_nc) as nc:
        assert test_good(nc), 'Not a good file'
        lwwn = get_lwwn_zf(nc)
        lwrad = get_lwrad(nc)
        dt = datetime.strptime(nc.date + nc.time, '%Y%m%d%H%M%S')
    return pd.DataFrame([lwrad], index=[dt], columns=lwwn)


zero_dimensional_variables = [
    u'new_aeri_ch1_original_laser_wavenumber',
    u'hatch_indicator',
    u'data_flag',
    u'aeri_ch1_original_laser_wavenumber',
    u'aeri_ch2_original_laser_wavenumber',
    u'shortwave_window_air_temp_2510_2515_mean',
    u'time_hi',
    u'time_lo',
    u'timeUTC',
    u'new_aeri_ch2_original_laser_wavenumber',
    u'surface_layer_air_temp_675_680_mean',
    u'min_lw_rms',
    u'shortwave_window_air_temp_2510_2515_std',
    u'longwave_window_air_temp_985_990_mean',
    u'clear_flag',
    u'longwave_window_air_temp_985_990_std',
    u'surface_layer_air_temp_675_680_std',
    u'min_sw_rms'
]


def get_lblrtm_data_frame(path_or_nc):
    with as_netcdf(path_or_nc) as nc:
        assert test_good(nc), 'Not a good file'
        lwwn = get_lwwn_zf(nc)
        lbl_lwrad = get_lbl_lwrad(nc)
        dt = datetime.strptime(nc.date + nc.time, '%Y%m%d%H%M%S')
    return pd.DataFrame([lbl_lwrad], index=[dt], columns=lwwn)


def get_zero_dimensional_frame(path_or_nc):
    with as_netcdf(path_or_nc) as nc:
        assert test_good(nc), 'Not a good file'
        dt = datetime.strptime(nc.date + nc.time, '%Y%m%d%H%M%S')
        try:
            return pd.DataFrame({key: nc.variables[key][:] for key in zero_dimensional_variables},
                                index=[dt])
        except Exception:
            return []


def get_difference(dataframe, wavenumber=900.):
    """
    Find the difference between aeri and lblrtm at a certain wavenumber
    """
    from bisect import bisect

    idx = bisect(dataframe['aeri'].columns, wavenumber)
    return dataframe.aeri.iloc[:, idx] - dataframe.lblrtm.iloc[:, idx]


def get_all_scalar_data(site_path):
    """
    Compile a dataframe for all of the data in site_path,
    this only includes scalar data
    """
    frames = pd.concat(map(get_zero_dimensional_frame, get_all_good_days(site_path, return_nc=True)))
    frames.sort_index(inplace=True)
    return frames


def get_all_good_days_rad(site_path):
    """
    Import all of the days in a site directory
    """
    try:
        return pd.concat(map(get_data_frame, get_all_good_days(site_path)))
    except Exception as e:
        if 'All objects passed were None' in str(e):
            LOG.warning('No good days')
            if glob(os.path.join(site_path, '*_out.cdf')) == []:
                LOG.warning('... no days at all')
            return
        else:
            raise


def get_all_good_days(site_path, return_nc=False):
    """
    Import all of the days in a site directory
    """
    paths = glob(site_path + '*_out.cdf')
    for path in paths:
        with as_netcdf(path) as nc:
            if test_good(nc):
                if return_nc:
                    yield nc
                else:
                    yield path


def get_all_uncertainty(site_path):
    """
    Get the uncertainty for an entire site
    """
    return pd.Series({s.index[0]: s[0] for s in pool.map(get_uncertainty_from_path, get_all_good_days(site_path))})


def get_all_difference(data_frame):
    return data_frame['aeri'].ix[:, 800:1200] - data_frame['lblrtm'].ix[:, 800:1200]


def get_uncertainty_from_path(path):
    return get_uncertainty(get_all_difference(get_data_frame(path)))


def get_uncertainty(difference_frame):
    """ John Gero's algorithm for determining new laser wavenumber uncertainty """
    difference_frame.ix[:, 900:1100] = pd.np.nan
    return pd.np.sqrt((difference_frame.ix[:, 800:1200]**2).mean(axis=1))


pool = Pool()

