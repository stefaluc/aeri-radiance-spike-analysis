__author__ = 'cphillips'

import unittest
from aeri_tools.io.dmv import radiance
from os.path import isdir,expanduser
import numpy.testing
import pandas as pd

import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)

def no_sample_data():
    return not isdir(expanduser('~/.aeri_tools/sample_data'))

clear_day_ch1 = expanduser('~/.aeri_tools/sample_data/clear_day/AE130618/130618C1.RNC')
clear_day_ch2 = expanduser('~/.aeri_tools/sample_data/clear_day/AE130618/130618C2.RNC')
clear_day_sum = expanduser('~/.aeri_tools/sample_data/clear_day/AE130618/130618.SUM')

@unittest.skipIf(no_sample_data(),'No clear day sample data')
class TestGetRadianceFromRNC(unittest.TestCase):

    def test_read_clear(self):
        rad = radiance.get_radiance_from_rnc(clear_day_ch1)
        self.assertEqual(rad.columns.size, 2655)
        self.assertEqual(len(rad.index.levels),2)
        self.assertEqual(rad.index.levels[0].name, 'time')
        rad2 = radiance.get_radiance_from_rnc(clear_day_ch2)
        self.assertEqual(rad2.columns.size, 2532)
        self.assertEqual(len(rad2.index.levels),2)
        self.assertEqual(rad2.index.levels[0].name, 'time')


clear_day = expanduser('~/.aeri_tools/sample_data/clear_day/AE130618')

@unittest.skipIf(no_sample_data(),'No clear day sample data')
class TestGetRadianceFromSpectrum(unittest.TestCase):

    def test_read_spectrum_clear(self):
        spec = radiance.get_spectrum_from_rnc(clear_day)
        self.assertGreater(spec.columns.max(),2000)
        self.assertLess(spec.columns.min(),1000)
        self.assertTrue((spec.columns == sorted(spec.columns)).all())

    def test_read_spectrum_fail(self):
        with self.assertRaises(EnvironmentError):
            radiance.get_spectrum_from_rnc(clear_day,date='20140101')

class TestZeroPadSpectrum(unittest.TestCase):

    def test_zero_pad(self):
        spec = radiance.get_spectrum_from_rnc(clear_day)
        zspec = radiance.zero_pad_spectrum(spec)
        self.assertEqual(zspec.columns[0],0)
        self.assertTrue((zspec.columns == sorted(zspec.columns)).all())
