from scipy.signal import gaussian

import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)

def apodize_aeri_spectrum(spectrum):
    windows = gaussian(1)
    apodized = None

    return apodized