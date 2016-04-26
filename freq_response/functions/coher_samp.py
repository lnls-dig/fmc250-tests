import math
from fractions import gcd

# Given a sampling frequency and a frequency signal, return the
# minimum sampling window for coherence (bigger than min_window)

def coher_samp(fsig,fs, min_window = 1):
    div = gcd(fsig,fs)
    min_coher = fs/div
    return math.ceil(min_window/min_coher)*min_coher
