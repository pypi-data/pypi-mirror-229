import numpy as np
from scipy.stats import t

# Learns an undirected independence graph from a given data set. The data are assumed to be normally distributed
# data : a data matrix with rows corresponding to observations and columns corresponding to random variables.
# p_value : the thresholding p-value for each conditional independence test.
def get_uig_norm(data, p_value):
    conmat = np.linalg.inv(np.corrcoef(data, rowvar=False))
    p = data.shape[1]
    n = data.shape[0]

    # cov2cor 
    d = np.sqrt(conmat.diagonal())
    parcor = ((conmat.T/d).T)/d
    parcor /= np.sqrt(np.outer(np.diag(parcor), np.diag(parcor)))
    t_stat = parcor * np.sqrt((n - p - 2) / (1 - parcor**2))
    thres = -t.ppf(p_value / 2, df=n - p - 2)
    amat = (np.abs(t_stat) > thres).astype(int)
    np.fill_diagonal(amat, 0)
    return amat