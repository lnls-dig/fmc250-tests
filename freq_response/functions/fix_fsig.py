from fractions import gcd

# Given a frequency signal "fsig", the sampling frequency "fs" and a
# sampling window "n_win", find the closes coherentfrequency to "fsig"

def fix_fsig(fsig, fs, n_win):
    div = gcd(fs, n_win)
    min_coher_freq = fs/div
    fixed_freq = round(fsig/min_coher_freq)*min_coher_freq
    # fix for case when fixed_freq == 0
    if (fixed_freq == 0):
        fixed_freq = min_coher_freq
    return fixed_freq
