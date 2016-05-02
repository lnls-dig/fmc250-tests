#!/usr/bin/python3

# Script to read and "data/power.txt" data files under "data/" and
# compute the power response over frequency.

import sys

import time

import numpy

import matplotlib.pyplot as pyplot

from functions.fourierseries import fourierseries

from configparser import SafeConfigParser

######################################################################
# Test Settings

config = SafeConfigParser()
config.read('config.ini')

num_samples = config.getint('Test','num_samples')
fs = config.getfloat('Test','fs') # sampling frequency in Hz


sys.stdout.write("\nRunning test...\n\n")

fund_power_array = []
fsig_array = []

######################################################################
# read power file

data = numpy.loadtxt('data/power.txt', delimiter = ',', skiprows = 1)

fsig_array = [d[0] for d in data]
fund_power_array = [d[1] for d in data]

power_array = []

for i in range(len(fund_power_array)):

    ##################################################################
    # Try to open the file
    try:
        data = numpy.loadtxt('data/file_freq_' + str(int(fsig_array[i])) + '.csv', delimiter = ',', skiprows = 1)
        data_time_array = [d[0] for d in data]
        data_amp_array = [d[1] for d in data]
    except:
        print("file_freq_" + str((fsig_array[i]))+ " not found...")
        exit()

    ##################################################################
    # Calculate fft

    fft_par = fourierseries(data_amp_array, fs)
    f = fft_par[1]
    fft = fft_par[0]

    # Scaling the data
    fft = 20*numpy.log10(fft)
    fft = fft - 20*numpy.log10(2**16-1) # Scale to full scale (16 bits)

    # find fundamental freq in fft and amplitude
    fft_max = numpy.amax(fft)
    fft_max_f = f[numpy.argmax(fft)]

    # normalize and save power of the fundamental freq according to
    # the first sampling frequency's power
    power_array.append(fft_max+fund_power_array[0]-fund_power_array[i])

######################################################################
# Generate plot and save in a PNG file

pyplot.plot(fsig_array, power_array)
pyplot.grid('on')
pyplot.title('Power delivered to ADC')
pyplot.ylabel('Power Normalized Magnetude [dBFS]')
pyplot.xlabel('Sampling Frequency [Hz]')
pyplot.savefig('power_fs.png')

print("\nok")
