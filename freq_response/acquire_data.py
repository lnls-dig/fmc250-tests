#!/usr/bin/python3

# Script to read and save data from ADCs at the frequencies in
# "freq.txt" in a subdirectory "data/". It also saves the power of the
# fundamental frequency in each frequency in the "data/powers.txt"

import sys
import os
import time
import numpy
import epics

from functions.fix_fsig import fix_fsig

import instr_tests


#################
# Test Settings #
#################

test_num = 0

afc_idn = 'SIDI-BPM-01-14'
sig_gen_ip = '10.0.18.34'
sig_gen_clk_ip = '10.0.18.50'
sig_ana_idn = 'DIG-RSFSV-0'

num_samples = 50000
fs = 240e6 # sampling frequency in Hz

######################################################################
# Initiate instruments

try:
    sig_gen = instr_tests.instruments.signal_generator.RSSMX100A_visa(sig_gen_ip)
except:
    sys.stdout.write("\nUnable to reach the signal generator (R&S SMB100A) through the " +
                     "network. Exiting...\n\n")
    exit()

try:
    sig_gen_clk = instr_tests.instruments.signal_generator.RSSMX100A_visa(sig_gen_clk_ip)
except:
    sys.stdout.write("\nUnable to reach the signal generator (R&S SMA100A) through the " +
                     "network. Exiting...\n\n")
    exit()

try:
    bpm = instr_tests.instruments.bpm.AFC_v3_1_epics(afc_idn)
except:
   sys.stdout.write("\nUnable to reach the BPM through the " +
                    "network. Exiting...\n\n")
   exit()

######################################################################
# Start test

sys.stdout.write("\nRunning test...\n\n")


# Setting clk generator

sig_gen_clk.set_fm('OFF') # turn off frequency modulation
sig_gen_clk.set_am(0)     # turn off amplitude modulation
sig_gen_clk.set_rf(fs, 7.9) # set RF signal frequency and level

time.sleep(1)

# read frequency file
with open('freq.txt','r') as fr:
    freq_array = fr.readlines()

# convert to float

for i in range(len(freq_array)):
    freq_array[i] = float(freq_array[i])

power_array = [] # initializing array that receives power of each freq

for i in range(len(freq_array)):
    print("Starting " + str(i) +"...")

    # fix freq to coherent sampling
    freq_array[i] = fix_fsig(freq_array[i], fs, num_samples)

    sig_gen.set_lfo(2000) # sets LF signal frequency
    sig_gen.set_fm('OFF') # turns off frequency modulation
    sig_gen.set_am(0)     # turns oFF amplitude modulation
    sig_gen.set_rf(freq_array[i], 7.9) # sets RF signal frequency and level

    file_name = 'data/file'

    ##################################################################
    # get raw points for s21 calculation

    time_array = numpy.array(range(num_samples))*1/fs # time array

    bpm.config_acq(num_samples, 0, 1, 'adc', 'now')

    time.sleep(2)

    data_array = bpm.get_arraydata('C', num_samples)

    # checks if directory exists. If not, create it.
    os.makedirs(os.getcwd() + "/" + os.path.dirname(file_name), exist_ok=True)

    with open(file_name + "_freq_"+ str(int(freq_array[i])) + '.csv','w') as fw:
        fw.write('t, y'+'\n') # Header
        for j in range(len(data_array)):
            fw.write(str(time_array[j]) + ", " + str(data_array[j]) + "\n")

    ##################################################################
    # Measure fundamental frequency power for the respective freq

    epics.caput(sig_ana_idn + ":GENERAL:Reset", 1)
    epics.caput(sig_ana_idn + ":FREQ:Span", 1e4)
    epics.caput(sig_ana_idn + ":FREQ:Center", freq_array[i])
    epics.caput(sig_ana_idn + ":GENERAL:SweMode", 0)

    time.sleep(1)

    epics.caput(sig_ana_idn + ":MARK:FindMax", 1)

    time.sleep(2)

    power_array.append(epics.caget(sig_ana_idn + ":MARK:Y_RBV"))

    print("... done!\n")

######################################################################
# Save the power array after the loop

with open('data/power' + '.txt','w') as fw:
    fw.write('t, y'+'\n') # Header
    for i in range(len(power_array)):
        fw.write(str(freq_array[i]) + ", " + str(power_array[i]) + "\n")

print("\nok")
