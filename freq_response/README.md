# FMC250 Analog Front-End Frequency Respose Test

## Description

This test intends to acquire the power response for the FMC250 analog
front-end.

### acquire_data.py file

The test uses two signal generators to generate clock and signal
frequency, reading the frequencies data from the "freq.txt" file,
adjusting them to the closest coherent frequency using
"functions/fix_fsig" and saving the amplitude and time data in the
subdirectory "data/". Since the power given by the signal generator
changes with the frequency, a signal analyzer was used to check the
power given at the fundamental frequency at each signal frequency and
save it on a "data/power.txt" so a normalization can be done.

### fft_plots.py file

This script retrieves the frequency data from "data/power.txt" and,
for each frequency, reads the respective data file and computes the
FFT with "functions/fourierseries.py". The estimated aliased frequency
is found with "functions/alias_freq", and the magnitude and frequency
data is plotted for each frequency, along with the aliased frequency.

### process_data.py file

This script uses the data acquired previously to generate an
power/frequency plot. It reads the data from "data/power.txt" and, for
each signal frequency, the respective data file is loaded. The fourier
series is computed with the "functions/fourierseries.py", the power of
the fundamental frequency is found and normalized according to the
"data/power.txt". After all this is done for all frequencies in
"data/power.txt", a plot is generated and saved in "power_fs.png".

## Running the test

### Setup

The scripts expect that all the required python packages used are
installed, including *PyEpics* and *PyVisa*. The [instr_tests][]
package was installed and used to communicate with the instruments.

[instr_tests]: https://github.com/lnls-dig/instr_tests

The instruments that are communicated via EPICS should already have
their IOCs connected to the network (in this case the only equipment
that uses EPICS is the [R&S FSV signal analyzer][])

[R&S FSV signal analyzer]: https://github.com/lnls-dig/rsfsv-epics-ioc

### Running

All the algorithms use python 3.x version. Firstly, the desired
frequencies should be written into the *freq.txt* file (don't worry
about coherence since the script will find and use the closest
coherent frequency to the input). Then run the *acquire_data.py* to
get the data, the *fft_plots.py* to generate the FFT plots for each of
the frequency datas and finally the *process_data.py* to get generate
the frequency response plot.
