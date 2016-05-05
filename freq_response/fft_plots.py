#####################################################################
# Importing packages

import matplotlib.pyplot as plt
import numpy
from configparser import SafeConfigParser

from functions.fourierseries import fourierseries
from functions.alias_freq import alias_freq

def to_full_scale(adc_resolution_bits, amp):
    amp = 20*numpy.log10(amp)
    return (amp - 20*numpy.log10(2**adc_resolution_bits-1))

def trim_phase(amp_threshold, phase, amp):
    phase_trim = phase
    # zero phase if amp is smaller than a threshold
    for idx, j in enumerate(amp):
        if j < amp_threshold:
            phase_trim[idx] = 0
    return phase_trim

def generate_plot(freq, amp, phase, f_alias):
    plt.close("all")
    ax1 = plt.subplot(211)
    plt.axvline(f_alias, color = 'r', label = "Aliased frequency")
    plt.plot(freq, amp)
    plt.grid('on')
    plt.title('FFT - Amplitude')
    plt.ylabel('Normalized Magnetude [dBFS]')
    plt.legend(loc = 'best')
    plt.ylim([-180, 0]) # empirical max values

    ax2 = plt.subplot(212)
    plt.plot(freq, phase)
    plt.grid('on')
    plt.title('FFT - Phase')
    plt.ylabel('Phase [degrees]')
    plt.xlabel('Frequency [Hz]')
    return plt

#####################################################################
# Main script

# Init
config = SafeConfigParser()
config.read('config.ini')

fs = config.getfloat('Test','fs') # sampling frequency in Hz
adc_resolution_bits = config.getint('Test','adc_resolution_bits')
amp_threshold = config.getfloat('Test','amp_threshold')
data_dir = config.get('Test','data_dir')
data_file_name = config.get('Test','data_file_name')
freq_file_name = config.get('Test','freq_file_name')
power_file_name = config.get('Test','power_file_name')

# Load power and frequency data
data = numpy.loadtxt(data_dir + power_file_name, delimiter = ',', skiprows = 1)
fsig_array = [d[0] for d in data]
fund_power_array = [d[1] for d in data]

# Generate fourier series for each frequency and plot
for i, power in enumerate(fund_power_array):

    data = numpy.loadtxt(data_dir + data_file_name + str(int(fsig_array[i])) + '.csv',
                         delimiter = ',', skiprows = 1)
    data_time_array = [d[0] for d in data]
    data_amp_array = [d[1] for d in data]

    fft_par = fourierseries(data_amp_array, fs)
    fft_amp = fft_par[0]
    fft_f = fft_par[1]
    fft_ph = fft_par[2]

    # Adjust amplitude and frequency to plot
    fft_amp_fs = to_full_scale(adc_resolution_bits, fft_amp)
    fft_ph_trim = trim_phase(amp_threshold, fft_ph, fft_amp_fs)

    f_alias = alias_freq(fsig_array[i],fs)

    plt = generate_plot(fft_f, fft_amp_fs ,fft_ph_trim, f_alias)
    plt.savefig(data_dir + data_file_name + str(int(fsig_array[i])) + '.png')
