from __future__ import division
__author__ = 'cphillips'
import quantities as pq
from quantities.constants import k,h


import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)

import numpy as np
import pandas as pd

c = pq.speed_of_light
c2 = (pq.speed_of_light.simplified)**2

aeri_output = pq.mW /((1/pq.cm)*pq.meter**2*pq.steradian)
RU_wl = pq.W / (pq.meter**2 *pq.meter*pq.steradian)
RU_wn = pq.W *pq.meter / (pq.meter**2 * pq.steradian)

def get_brightness_temps(radiance_df, aeri_wavenumber_units=(1/pq.cm), aeri_rad_units=aeri_output):
    """
    Get brightness temperatures given a pandas dataframe
    :param radiance_df: DataFrame
    :return: DataFrame of brightness temperatures
    """
    rad = _get_radiance_wl(radiance_df,default_units=aeri_rad_units)
    temps = get_brightness_temp_wn(rad,radiance_df.columns.values*aeri_wavenumber_units)

    return pd.DataFrame(temps,index=radiance_df.index,columns=radiance_df.columns)

def get_brightness_temp_wn(radiance,wavenumber,emissivity=1):
    """
    Get the brightness temperature given a wavenumber and radiance
    :param radiance: radiance with respect to wavenumber
    :param wavenumber:
    :param emissivity:
    :return:

    >>> 278 < get_brightness_temp_wn(70*aeri_output,990/pq.cm) < 279
    True
    """

    radiance = _get_radiance_wn(radiance)

    return (h*c/k*wavenumber).simplified/np.log(1+(2*h*c2 / radiance * wavenumber**3 ).simplified)

def get_brightness_temp_wl(radiance,wavelength,emissivity=1):
    """
    Get the brightness temperature given a wavelength and radiance
    :param radiance: radiance with respect to wavelength
    :param wavelength:
    :param emissivity:
    :return:

    >>> 299 < get_brightness_temp_wl(3.7217e6*RU_wl,500/pq.cm) < 300
    True
    """

    radiance = _get_radiance_wl(radiance)

    # Use wavelength equation
    wavelength = _get_wavelength(wavenumber=wavelength)
    return (h*c/k/wavelength).simplified/np.log(1+(2*h*c2 / radiance / wavelength**5 ).simplified)

def get_radiance_from_bt(temperature,wavelength):
    t1 = np.exp((h*c/wavelength/k/temperature).simplified)-1
    return (2*h*c2/(wavelength**5* t1)).simplified


def _get_radiance_wl(radiance, default_units=RU_wl):
    """
    Assure the radiance has units
    :param radiance: numpy.ndarray
    :return: radiance ndarray with units
    """
    # Add units
    return pq.Quantity(radiance,default_units)

def _get_radiance_wn(radiance, default_units=aeri_output):
    """
    Assure the radiance has units
    :param radiance: numpy.ndarray
    :return: radiance ndarray with units
    """
    # Add units
    return pq.Quantity(radiance,default_units)

def _get_wavelength(wavenumber=None,wavelength=None,frequency=None):
    """
    Convert to wavelength
    :param wavenumber: Optional wavenumber (m^-1)
    :param wavelength: Optional wavelength (m)
    :param frequency: Optional frequency in units Hz
    :return: wavelength in units m

    >>> _get_wavelength(wavenumber=500./pq.cm) == 2e-5*pq.m
    True
    >>> _get_wavelength(wavelength=5) == 5*pq.m
    True
    >>> _get_wavelength(frequency=float(c.simplified)) == 1*pq.m
    True
    """

    # Convert from wavelength
    if wavelength is not None:
        # Add units if it doesn't have them
        return pq.Quantity(wavelength,pq.meter)

    # Convert from wavenumber
    elif wavenumber is not None:
        wavenumber = pq.Quantity(wavenumber,1/pq.meter)
        return (1/wavenumber).simplified


    # Convert from frequency
    elif frequency is not None:
        frequency = pq.Quantity(frequency, pq.Hz)
        return (pq.speed_of_light/frequency).simplified

def _get_frequency(wavenumber=None,wavelength=None,frequency=None):
    """
    Convert to frequency
    :param wavenumber: Optional wavenumber (m^-1)
    :param wavelength: Optional wavelength (m)
    :param frequency: Optional frequency in units Hz
    :return: wavelength in units m
    """
    return (pq.speed_of_light/_get_wavelength(wavenumber=wavenumber,
                                                      wavelength=wavelength,
                                                      frequency=frequency)).simplified
