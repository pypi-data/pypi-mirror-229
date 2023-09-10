from .junctiontree import SepPair
from .norm_ci_test import gaussCItest
from .pattern import get_pattern_matrix
from scipy.stats import chi2
from .calculate_deviance import dev_ci_test

import numpy as np

# Learns a complexs using a skeleton and covariance matrix.
# skel: Skeleton containing 'amat' and 'sep.pairs' information.
# cov: Covariance matrix.
# n: Size of the data sample.
# p_value: Threshold p-value for significance.
def learn_complex_norm(skel, cov, n, p_value):
    wmat = skel["amat"]
    sep_pairs = skel["sep_pairs"]
    n_sep = len(sep_pairs)

    d = np.sqrt(cov.diagonal())
    parcor = ((cov.T/d).T)/d
    stuffStat = {'C' : parcor, 'n' : n}

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
                    calculated_pval = gaussCItest(u, v, new_sep, stuffStat)
                    degrees_of_freedom = 1  # Replace with the appropriate degrees of freedom for your chi-square distribution
                    chi_value = dev_ci_test(cov, cov.shape[0], n, u, v, new_sep, len(new_sep))
                    # chi_value = chi2.ppf(1 - calculated_pval, degrees_of_freedom)
                    if calculated_pval < p_value and (-1 - chi_value) < wmat[w, u]:
                        wmat[w, u] = -1 - chi_value
    idx = np.where(wmat - wmat.T < 0)
    wmat[idx] = 0
    wmat = 0 + (wmat != 0)
    pat = get_pattern_matrix(wmat)
    pat = pat[::-1, ::-1]
    return pat
