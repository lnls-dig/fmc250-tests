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

data = numpy.loadtxt('data/power.txt', delimiter = ',', skiprows = 1)

fsig_array = [d[0] for d in data]
fund_power_array = [d[1] for d in data]

######################################################################
#  Read and process files for each frequency

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
