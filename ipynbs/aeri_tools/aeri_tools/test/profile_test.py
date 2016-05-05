__author__ = 'cphillips'

import unittest
from aeri_tools.io.aeriprof import profile
from os.path import isdir, expanduser

import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)


clear_day_prof = expanduser('~/.aeri_tools/sample_data/clear_day_prof/20130618AP.cdf')
cloudy_day_prof = expanduser('~/.aeri_tools/sample_data/cloudy_day_prof/20150225AP.cdf')


@unittest.skipIf(not isdir(expanduser('~/.aeri_tools/sample_data')),'No clear day sample data')
class TestGetPanel(unittest.TestCase):

    def test_clear_day_profile(self):
        ap = profile.get_panel(clear_day_prof)
        self.assertIn('pressure',ap)
        self.assertIn('ambientTemp',ap)
        self.assertIn('WaterVaporMixingRatio',ap)
