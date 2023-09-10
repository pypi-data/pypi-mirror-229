import numpy as np
from scipy.stats import norm

# Compute the z-statistic for partial correlation.
# - x, y: Indices of variables for which to compute the z-statistic.
# - S: Set of conditioning variables.
# - C: Correlation matrix among variables.
# - n: Sample size.
def zStat(x, y, S, C, n):
    r = pcorOrder(x, y, S, C)
    res = np.sqrt(n - len(S) - 3) * 0.5 * np.log((1+r)/(1-r))
    return 0 if np.isnan(res) else res

# Check if the Fisher-transformed partial correlation coefficient is within the cutoff range.
# - x, y: Indices of variables for which to compute the Fisher-transformed partial correlation coefficient.
# - S: Set of conditioning variables.
# - C: Correlation matrix among variables.
# - n: Sample size.
# - cutoff: Upper and lower bounds for the Fisher-transformed partial correlation coefficient.
def condIndFisherZ(x, y, S, C, n, cutoff, verbose=False):
    r = pcorOrder(x, y, S, C)
    res = np.sqrt(n - len(S) - 3) * 0.5 * np.log((1+r)/(1-r))
    return np.isnan(res) or np.abs(res) <= cutoff

# Perform the Gaussian conditional independence test.
# - x, y: Indices of variables for which to perform the test.
# - S: Set of conditioning variables.
# - stuffStat: Dictionary containing relevant statistical information.
def gaussCItest(x, y, S, stuffStat):
    z = zStat(x, y, S, C=stuffStat['C'], n=stuffStat['n'])
    p_value = 2 * (1 - norm.cdf(abs(z)))
    return p_value


# Compute partial correlation coefficient.
# - i, j, k: Indices of variables for which to compute the partial correlation coefficient.
# - C: Correlation matrix among variables.
# - cut_at: Upper and lower bounds for the partial correlation coefficient.

def pcorOrder(i, j, k, C, cut_at=0.9999999):
    
    if len(k) == 0:
        r = C[i, j]
    elif len(k) == 1:
        r = (C[i, j] - C[i, k[0]] * C[j, k[0]]) / np.sqrt((1 - C[j, k[0]]**2) * (1 - C[i, k[0]]**2))
    else:
        variables = [i, j] + [x for x in k]
        PM = np.linalg.pinv(C[variables, :][:, variables]) #psusedoinverse
        r = -PM[0, 1] / np.sqrt(PM[0, 0] * PM[1, 1])
    if np.isnan(r):
        return 0
    else:
        return min(cut_at, max(-cut_at, r))
