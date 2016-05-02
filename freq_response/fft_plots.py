#####################################################################
# Importing packages

import matplotlib.pyplot as plt
import numpy
from configparser import SafeConfigParser

from functions.fourierseries import fourierseries
from functions.alias_freq import alias_freq

#####################################################################
# Configuring the parameters

config = SafeConfigParser()
config.read('config.ini')

fs = config.getfloat('Test','fs') # sampling frequency in Hz

######################################################################
# read power file

fund_power_array = []
fsig_array = []

with open('data/power.txt','r') as fr:
    lines = fr.readlines()

for i in range(1,len(lines)):  # start from 1 to avoid header
    temp_i = lines[i].split(',')
    fsig_array.append(temp_i[0])
    fund_power_array.append(temp_i[1])

# convert to float

for i in range(len(fsig_array)):
    fsig_array[i] = float(fsig_array[i])
    fund_power_array[i] = float(fund_power_array[i])


######################################################################
#  Read and process files for each frequency

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

    for j in range(len(data_time_array)):
        data_time_array[j] = float(data_time_array[j])
        data_amp_array[j] = float(data_amp_array[j])

    ##################################################################
    # Calculate fft

    fft_par = fourierseries(data_amp_array, fs)

    fft_amp = fft_par[0]
    fft_f = fft_par[1]
    fft_ph = fft_par[2]

    ##################################################################
    # Scaling the data
    fft_amp = 20*numpy.log10(fft_amp)
    fft_amp = fft_amp - 20*numpy.log10(2**16-1) # Scale to full scale (16 bits)


    # zero phase if amp is smaller than a threshold
    for idx, j in enumerate(fft_amp):
        if j < -90:
            fft_ph[idx] = 0

    ##################################################################
    # Calculating the aliased frequency

    f_alias = alias_freq(fsig_array[i],fs)

    ##################################################################
    # Plotting the data

    plt.close("all")
    ax1 = plt.subplot(211)
    plt.axvline(f_alias, color = 'r', label = "Aliased frequency")
    plt.plot(fft_f, fft_amp)
    plt.grid('on')
    plt.title('FFT - Amplitude')
    plt.ylabel('Normalized Magnetude [dBFS]')
    #plt.xlabel('Frequency [Hz]')
    plt.legend(loc = 'best')
    plt.ylim([-180, 0]) # empirical data

    ax2 = plt.subplot(212)
    plt.plot(fft_f, fft_ph)
    plt.grid('on')
    plt.title('FFT - Phase')
    plt.ylabel('Phase [degrees]')
    plt.xlabel('Frequency [Hz]')
    plt.ylim([-4, 4]) # empirical data

    plt.savefig('data/fft_freq_' + str(int(fsig_array[i])) + '.png')
