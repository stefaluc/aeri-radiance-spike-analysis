__author__ = 'cphillips'

import netCDF4

import pandas as pd

from aeri_tools.io.util import get_times_from_hours, get_dates_from_yymmdd, get_datetime_index


def read_netcdf(filename):
    ds = netCDF4.Dataset(filename)

    if 'Ch1BackwardScanRealPartCounts' in ds.variables:
        rad_real = ds.variables['Ch1BackwardScanRealPartCounts'][:]
        wave_number = ds.variables['Ch1BackwardScanRealPartCounts_ind'][:]
        rad_imaginary = ds.variables['Ch1BackwardScanImagPartCounts'][:]
    elif 'Ch1ForwardScanRealPartCounts' in ds.variables:
        rad_real = ds.variables['Ch1ForwardScanRealPartCounts'][:]
        wave_number = ds.variables['Ch1ForwardScanRealPartCounts_ind'][:]
        rad_imaginary = ds.variables['Ch1ForwardScanImagPartCounts'][:]
    elif 'Ch2BackwardScanRealPartCounts' in ds.variables:
        rad_real = ds.variables['Ch2BackwardScanRealPartCounts'][:]
        wave_number = ds.variables['Ch2BackwardScanRealPartCounts_ind'][:]
        rad_imaginary = ds.variables['Ch2BackwardScanImagPartCounts'][:]
    elif 'Ch2ForwardScanRealPartCounts' in ds.variables:
        rad_real = ds.variables['Ch2ForwardScanRealPartCounts'][:]
        wave_number = ds.variables['Ch2ForwardScanRealPartCounts_ind'][:]
        rad_imaginary = ds.variables['Ch2ForwardScanImagPartCounts'][:]
    else:
        raise NotImplemented

    times = get_times_from_hours(ds.variables['Time'][:])
    dates = get_dates_from_yymmdd(ds.variables['dateYYMMDD'][:])

    datetime_index = get_datetime_index(dates, times)
    ds.close()
    return pd.DataFrame(rad_real + 1j * rad_imaginary, index=datetime_index, columns=wave_number)
