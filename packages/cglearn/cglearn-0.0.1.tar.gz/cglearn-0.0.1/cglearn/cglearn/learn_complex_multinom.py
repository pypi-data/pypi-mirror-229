from .junctiontree import SepPair
from .multinom_ci_test import multinom_ci_test
from .pattern import get_pattern_matrix
import numpy as np

# Learns a complexs using a skeleton and covariance matrix.
# skel: Skeleton containing 'amat' and 'sep.pairs' information.
# cov: Covariance matrix.
# n: Size of the data sample.
# p_value: Threshold p-value for significance.
def learn_complex_multinom(skel, freq_tb, p_value):
    wmat = skel["amat"]
    sep_pairs = skel["sep_pairs"]
    n_sep = len(sep_pairs)

    if n_sep == 0:
        return wmat
    for i in range(n_sep):
        pair:SepPair = sep_pairs[i]
        for turn in range(2):
            u = pair.u if turn == 0 else pair.v
            v = pair.v if turn == 0 else pair.u
            sep = pair.s
            row = wmat[u]
            nb_u = np.where(row == 1)[0]
            nb_u_size = len(nb_u)
            if nb_u_size > 0:
                for j in range(nb_u_size):
                    w = nb_u[j]
                    new_sep = np.unique(np.append(sep, w)).astype(int)
                    res = multinom_ci_test(freq_tb, u, v, new_sep)
                    calculated_pval = res["pval"]
                    chi_value = res["dev"]
                    if calculated_pval < p_value and (-1 - chi_value) < wmat[w, u]:
                        wmat[w, u] = -1 - chi_value
    idx = np.where(wmat - wmat.T < 0)
    wmat[idx] = 0
    wmat = 0 + (wmat != 0)
    return get_pattern_matrix(wmat)
