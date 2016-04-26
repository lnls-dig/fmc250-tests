import numpy as np

# Given a sample frequency and a signal frequency, return the
# frequency that signal frequency will be aliased to.
def alias_freq(f_signal,f_sample):
    n = round(f_signal / float(f_sample))
    f_alias = np.abs((f_sample-1)*n - f_signal)
    return f_alias
