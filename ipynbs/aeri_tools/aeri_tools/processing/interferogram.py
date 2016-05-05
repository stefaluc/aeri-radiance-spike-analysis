__author__ = 'cphillips'

import pandas as pd
import numpy as np
from numpy.fft import ifftshift, fftshift, irfft, rfft, fftfreq, rfftfreq

from aeri_tools.io.dmv.radiance import zero_pad_spectrum


def get_interferogram_from_spectrum(spectrum):
    spectrum = zero_pad_spectrum(spectrum)
    ifgs = ifftshift(irfft(spectrum, axis=1), axes=1)
    freqs = ifftshift(fftfreq(ifgs.shape[1], d=spectrum.columns.max() / len(spectrum.columns)))
    freqs -= np.median(freqs)
    return pd.DataFrame(ifgs, index=spectrum.index, columns=freqs).sort_index(axis=1)


def get_spectrum_from_interferogram(interferogram):
    specs = rfft(fftshift(interferogram, axes=1), axis=1)
    fs = (interferogram.columns.max() - interferogram.columns.min()) / (len(interferogram.columns) + 1)
    columns = rfftfreq(len(interferogram.columns), d=fs)
    return pd.DataFrame(specs, index=interferogram.index, columns=columns).sort_index(axis=1)
