import numpy as np
from scipy.stats import ks_2samp


def ks_test(a, b):
    ''' the KS test between two probability distributions'''
    return ks_2samp(a, b)


def trace_distance(a, b):
    ''' trace distance between two probability distributions [Nielsen and Chuang] '''
    return 1 - np.sum(np.abs(a - b)) / 2.


def fidelity(a, b):
    ''' the classical fidelity between two probability distributions [Nielsen and Chuang] '''
    return np.sum(np.sqrt(a * b))


def similarity(a, b):
    ''' the similarity between two probability distributions '''
    return fidelity(a, b) ** 2
