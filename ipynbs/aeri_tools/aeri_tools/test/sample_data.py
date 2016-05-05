__author__ = 'cphillips'

import os
from os.path import isdir
import subprocess

import logging
logging.basicConfig(level=logging.DEBUG,format='%(levelname)s: %(message)s')
LOG = logging.getLogger(__name__)

SAMPLE_DATA_ROOT = os.path.expanduser('~/.aeri_tools/')

def download(data_root=SAMPLE_DATA_ROOT):
    data_root = os.path.join(data_root,'')
    if not isdir(data_root):
        os.makedirs(data_root)
    subprocess.check_call(['rsync','-a','dreadnaught.ssec.wisc.edu::data/home/cphillips/sample_data',data_root])


if __name__ == '__main__':
    download()
