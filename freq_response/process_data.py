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

with open('data/power.txt','r') as fr:
    lines = fr.readlines()

for i in range(1,len(lines)):  # start from 1 to avoid header
    temp_i = lines[i].split(',')
    fsig_array.append(temp_i[0])
    fund_power_array.append(temp_i[1])

# convert to float
fsig_array = [float(freq) for freq in fsig_array]
fund_power_array = [float(power) for power in fund_power_array]

power_array = []

for i in range(len(fund_power_array)):

    data_time_array = []
    data_amp_array = []

    ##################################################################
    # Try to open the file
    try:
        with open("data/file_freq_" + str(int(fsig_array[i])) + '.csv','r') as fr:
            lines = fr.readlines()
    except:
        print("file_freq_" + str((fsig_array[i]))+ " not found...")
        exit()

    for j in range(1,len(lines)): # start from 1 to avoid header
        temp_j = lines[j].split(',')
        data_time_array.append(temp_j[0])
        data_amp_array.append(temp_j[1])

    # convert to float
    data_time_array = [float(time) for time in data_time_array]
    data_amp_array = [float(amp) for amp in data_amp_array]

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
