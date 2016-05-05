import numpy as np
import pandas as pd
from netCDF4 import Dataset
from ..util import as_netcdf
import pytz

import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)


def get_metadata(path_or_netcdf):
    with as_netcdf(path_or_netcdf) as ds:
        columns = {}
        for var in ds.variables:
            if ds.variables[var].dimensions == ('time',):
                columns[var] = ds.variables[var][:]
            if ds.variables[var].dimensions == ():
                columns[var] = ds.variables[var][:]
        return pd.DataFrame(columns)

def get_index(path_or_netcdf):
    with as_netcdf(path_or_netcdf) as ds:
        metadata = get_metadata(ds)
        try:
            times = pd.to_timedelta(metadata.AERItime,unit='h')
        except AttributeError:
            times = pd.to_timedelta(metadata.Time,unit='h')
        try:
            dates = pd.to_datetime(metadata.Date,format='%Y%m%d')
            datetimes = times+dates
        except AttributeError:
            datetimes = times
        return pd.DatetimeIndex(datetimes,tz=pytz.UTC)


def get_dataframe(path_or_netcdf,variable_name):
    with as_netcdf(path_or_netcdf) as ds:
        index = get_index(ds)
        return pd.DataFrame(ds.variables[variable_name][:],index=index).replace(-9999.,np.nan)


def get_panel(path_or_netcdf,variables=None):
    if not variables:
        variables = ['ambientTemp','WaterVaporMixingRatio','dewpointTemp','pressure','height']
    with as_netcdf(path_or_netcdf) as ds:
        dataframes = {key:get_dataframe(ds,key) for key in variables}
    panel = pd.Panel(dataframes)
    return panel

def level_panel_pressure(panel):
    reverse_mean_pressure = panel.pressure.mean(axis=0)[::-1]
    norm = lambda x: pd.Series(np.interp(reverse_mean_pressure,panel.pressure.ix[x.name,::-1],x[::-1])[::-1])
    ambientTemp = panel.ambientTemp.apply(norm,axis=1,broadcast=True)
    WaterVaporMixingRatio = panel.WaterVaporMixingRatio.apply(norm,axis=1,broadcast=True)
    dewpointTemp = panel.dewpointTemp.apply(norm,axis=1,broadcast=True)
    new_panel = pd.Panel({'ambientTemp':ambientTemp,'WaterVaporMixingRatio':WaterVaporMixingRatio,'dewpointTemp':dewpointTemp})
    new_panel.set_axis(2,reverse_mean_pressure[::-1])
    return new_panel

def level_panel_height(panel):
    mean_height = panel.height.mean(axis=0)
    norm = lambda x: pd.Series(np.interp(mean_height,panel.height.ix[x.name],x))
    ambientTemp = panel.ambientTemp.apply(norm,axis=1,broadcast=True)
    WaterVaporMixingRatio = panel.WaterVaporMixingRatio.apply(norm,axis=1,broadcast=True)
    dewpointTemp = panel.dewpointTemp.apply(norm,axis=1,broadcast=True)
    new_panel = pd.Panel({'ambientTemp':ambientTemp,'WaterVaporMixingRatio':WaterVaporMixingRatio,'dewpointTemp':dewpointTemp})
    new_panel.set_axis(2,mean_height)
    return new_panel

RATIO_VALUES_RANGE= np.arange(0, 15, .5)
TEMP_VALUES_RANGE= np.arange(235, 305, 1)
HUMID_VALUES_RANGE = np.arange(0, 100, 5)
PTEMP_VALUES_RANGE= np.arange(275, 345, 1)