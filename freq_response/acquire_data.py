#!/usr/bin/python3

# Script to read and save data from ADCs at the frequencies in
# "freq.txt" in a subdirectory "data/". It also saves the power of the
# fundamental frequency in each frequency in the "data/powers.txt"

import sys
import os
import time
import numpy
import epics
from configparser import SafeConfigParser

from functions.fix_fsig import fix_fsig

import instr_tests


######################################################################
# Functions

def init_instruments(sig_gen_config, sig_gen_clk_config, bpm_config):
    # arguments are in a dictionary of lists, containing the ip/idn on
    # the first element and the protocol in the second element

    if sig_gen_config[1] == 'visa':
        sig_gen = instr_tests.instruments.signal_generator.RSSMX100A_visa(sig_gen_config[0])
    elif sig_gen_config[1] == 'epics':
        sig_gen = instr_tests.instruments.signal_generator.RSSMX100A_epics(sig_gen_config[0])


    if sig_gen_clk_config[1] == 'visa':
        sig_gen_clk = instr_tests.instruments.signal_generator.RSSMX100A_visa(sig_gen_clk_config[0])
    elif sig_gen_clk_config[1] == 'epics':
        sig_gen_clk = instr_tests.instruments.signal_generator.RSSMX100A_epics(sig_gen_clk_config[0])


    if bpm_config[1] == 'visa':
        print("AFC in visa NOT implemented, only available by EPICS")
    elif bpm_config[1] == 'epics':
        bpm = instr_tests.instruments.bpm.AFC_v3_1_epics(bpm_config[0])

    return sig_gen, sig_gen_clk, bpm

def create_data_dir(data_dir):
    # checks if data subdirectory exists. If not, create it.
    os.makedirs(os.getcwd() + "/" + os.path.dirname(data_dir), exist_ok=True)

def set_clk_freq(sig_gen_clk, sig_gen_clk_level, freq):
    # Configure instrument that generates the clock
    sig_gen_clk.set_fm('OFF')
    sig_gen_clk.set_am('OFF')
    sig_gen_clk.set_rf(freq, sig_gen_clk_level)

    time.sleep(1) # wait due to set command above

def set_sig_freq(sig_gen, sig_gen_level, freq):
    # Configure instrument that generates the input signal
    sig_gen.set_fm('OFF')
    sig_gen.set_am('OFF')
    sig_gen.set_rf(freq, sig_gen_level)

def get_sig_power(sig_ana_idn, freq):
    epics.caput(sig_ana_idn + ":GENERAL:Reset", 1)
    epics.caput(sig_ana_idn + ":FREQ:Span", 1e4)
    epics.caput(sig_ana_idn + ":FREQ:Center", freq)
    epics.caput(sig_ana_idn + ":GENERAL:SweMode", 0)

    time.sleep(1) # time delay to enable the signal analyzer to set
                  # the configurations

    epics.caput(sig_ana_idn + ":MARK:FindMax", 1)

    time.sleep(2) # time delay between data request and data acquisition

    return epics.caget(sig_ana_idn + ":MARK:Y_RBV")


######################################################################
# Main script

# Init

config = SafeConfigParser()
config.read('config.ini')

data_dir = config.get('Test','data_dir')
data_file_name = config.get('Test','data_file_name')
freq_file_name = config.get('Test','freq_file_name')
power_file_name = config.get('Test','power_file_name')
sig_gen_ip = config.get('IP','sig_gen_ip')
sig_gen_clk_ip = config.get('IP','sig_gen_clk_ip')
afc_idn = config.get('EPICS_IDN','afc_epics_idn')
sig_ana_idn = config.get('EPICS_IDN','sig_ana_epics_idn')
num_samples = config.getint('Test','num_samples')
fs = config.getfloat('Test','fs')
adc_resolution_bits = config.getint('Test','adc_resolution_bits')
sig_gen_level = config.get('Test','sig_gen_level')
sig_gen_clk_level = config.get('Test','sig_gen_clk_level')
bpm_channel = config.get('Test','bpm_channel')

power_array = [] # initializing array that receives power of each freq

sig_gen, sig_gen_clk, bpm = init_instruments(sig_gen_config = [sig_gen_ip,'visa'],
                                             sig_gen_clk_config = [sig_gen_clk_ip, 'visa'],
                                             bpm_config = [afc_idn,'epics'])

create_data_dir(data_dir)

sys.stdout.write("\nRunning test...\n\n")

set_clk_freq(sig_gen_clk, sig_gen_clk_level, fs)

freq_array = numpy.loadtxt(freq_file_name)

# fix input frequencies to coherent sampling, using the closes
# coherent frequency
freq_array = [fix_fsig(freq, fs, num_samples) for freq in freq_array]

# Generates one test and file for each input frequency
for i, freq in enumerate(freq_array):

    print("Starting " + str(i) +"...")

    set_sig_freq(sig_gen, sig_gen_level, freq)

    time_array = numpy.array(range(num_samples))*1/fs # generate time array

    bpm.config_acq(num_samples, 0, 1, 'adc', 'now')
    time.sleep(2) # time delay to let BPM do the acquisition
    data_array = bpm.get_arraydata(bpm_channel, num_samples)


    data = numpy.column_stack((time_array,data_array)) # Format data into 2 columns
    numpy.savetxt(data_dir + data_file_name + str(int(freq)) + '.csv',
                  data, header = 't, counts (max ' + str(adc_resolution_bits) + ' bits)',delimiter = ',')

    # Measure fundamental frequency power for the respective freq
    sig_power = get_sig_power(sig_ana_idn, freq)
    power_array.append(sig_power)
    print("... done!\n")


data = numpy.column_stack((freq_array, power_array)) # Format data into 2 columns
numpy.savetxt(data_dir + power_file_name, data, delimiter = ',', header = 'Hz, dBm')

print("\nok")
