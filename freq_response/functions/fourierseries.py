#-----------------------------------------------------------------------------
# Title      : Fourier Series
# Project    :
#-----------------------------------------------------------------------------
# File       : fourierseries.py
# Author     : Vitor Finotti Ferreira  <vfinotti@finotti-Inspiron-7520>
# Company    : Brazilian Synchrotron Light Laboratory, LNLS/CNPEM
# Created    : 2016-03-28
# Last update: 2016-03-28
# Platform   :
# Standard   : Python 3.4
#-----------------------------------------------------------------------------
# Description:
#
# Implements a fourier series of a time series. The algorithm was based on
# "samplefourier.m" made by Daniel Tavares, available on
# https://github.com/lnls-dig/libdsp/blob/master/fourierseries.m
#-----------------------------------------------------------------------------
# Copyright (c) 2016 Brazilian Synchrotron Light Laboratory, LNLS/CNPEM
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Revisions  :
# Date        Version  Author          Description
# 2016-mar-28 1.0      vfinotti        Created
#-----------------------------------------------------------------------------

import numpy as np
from scipy.fftpack import fft

def fourierseries(data, Fs = 1, window = []): # declare function and default values
    """
    FOURIERSERIES   Fourier series of a time series.
    [fft_amplitude, f, fft_phase] = FOURIERSERIES(data, Fs, window)"""

    # transform lists to numpy arrays
    data = np.array(data,ndmin=2)
    window = np.array(window,ndmin=2)

    if 1 in np.shape(data):
        data = data.reshape((np.size(data),1)) # reshape into an array

    npts = data.shape[0];

    if window.size == 0:
        window = np.ones(np.shape(data)[0]) # create rectangular window

    window = window.reshape((np.size(window),1)) # reshape into an array

    data = np.multiply(data,np.tile(window,(1,np.shape(data)[1])))

    # get fft amplitude and phase, tranposing to compute the fft function (python convention)
    amp = np.abs(fft(data.transpose()))/npts # get normalized fft amplitude
    ph = np.angle(fft(data.transpose()))

    # transpose back to regular convention (data on columns)
    amp = amp.transpose()
    ph = ph.transpose()

    # get spectrum until fs/2
    half_npts = np.ceil((npts+1)/2)
    amp = amp[:half_npts]
    ph = ph[:half_npts]

    # correct the amplitude doubling the amp, except for the DC value
    if npts%2 > 0:
        amp = np.vstack((amp[0],2*amp[1:]))
    else:
        amp = np.vstack((amp[0],2*amp[1:-1],amp[-1]))

    # create frequency array
    df = Fs/npts
    f = np.arange(half_npts)*df

    f = f.reshape((np.size(f),1))

    return (amp,f,ph)
