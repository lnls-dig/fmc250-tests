#!/usr/bin/python3

# Script to compute the power response over frequency of the ADC
# front-end using the data acquired using the "acquire_data" script.

import sys
import time
import numpy
import matplotlib.pyplot as pyplot
from functions.fourierseries import fourierseries
from configparser import SafeConfigParser

######################################################################
# Functions

def to_full_scale(adc_resolution_bits, amp):
    # convert to full scale using the adc resulution
    amp = 20*numpy.log10(amp)
    return (amp - 20*numpy.log10(2**adc_resolution_bits-1))

def fund_freq_amp(amp):
    # find fundamental frequency amplitude
    amp_max = numpy.amax(amp)
    return amp_max

def generate_plot(freq, power):
    pyplot.close('all')
    pyplot.plot(freq, power)
    pyplot.grid('on')
    pyplot.title('Power delivered to ADC')
    pyplot.ylabel('Power Normalized Magnetude [dBFS]')
    pyplot.xlabel('Sampling Frequency [Hz]')
    return pyplot

######################################################################
# Main script

config = SafeConfigParser()
config.read('config.ini')

data_dir = config.get('Test','data_dir')
data_file_name = config.get('Test','data_file_name')
power_file_name = config.get('Test','power_file_name')
power_plot_name = config.get('Test','power_plot_name')
num_samples = config.getint('Test','num_samples')
fs = config.getfloat('Test','fs') # sampling frequency in Hz
adc_resolution_bits = config.getint('Test','adc_resolution_bits')

sys.stdout.write("\nRunning test...\n\n")

# Initialize arrays that will receive data in each loop cycle
fund_power_array = []
fsig_array = []


# Load power and frequency data
data = numpy.loadtxt(data_dir + power_file_name, delimiter = ',', skiprows = 1)
fsig_array = [d[0] for d in data]
fund_power_array = [d[1] for d in data]

power_array = []

for i, power in enumerate(fund_power_array):

    data = numpy.loadtxt(data_dir + data_file_name + str(int(fsig_array[i])) + '.csv',
                         delimiter = ',', skiprows = 1)
    data_time_array = [d[0] for d in data]
    data_amp_array = [d[1] for d in data]

    fft_par = fourierseries(data_amp_array, fs)
    f = fft_par[1]
    fft_amp = fft_par[0]

    fft_amp_fs = to_full_scale(adc_resolution_bits, fft_amp)

    fft_max = fund_freq_amp(fft_amp_fs)

    # normalize and save power of the fundamental freq according to
    # the first sampling frequency's power
    power_array.append(fft_max+fund_power_array[0]-fund_power_array[i])


pyplot = generate_plot(fsig_array, power_array)
pyplot.savefig(power_plot_name)

print("\nok")
