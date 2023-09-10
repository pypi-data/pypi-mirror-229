import numpy as np
from scipy.stats import multivariate_normal
from .is_chain_graph import is_chain_graph

def rnorm_cg(n, amat, Bstar, corderBstar):
    output = is_chain_graph(amat)
    if not output['result']:
        raise ValueError("The input should be a chain graph!")
    
    p = amat.shape[0]
    corder = np.flip(output["vert_order"])
    csize = np.flip(output["chain_size"])
    
    np.fill_diagonal(amat, 1)
    
    if not np.all(corderBstar == corder) or not np.all((Bstar.T == 0) == (amat[corder][:, corder] == 0)):
        raise ValueError("The Bstar and amat are not compatible!")
    
    b = np.cumsum(csize)
    W = np.zeros((p, n))
    
    for k in range(len(csize)):
        if k == 0:
                prevK = 0
        else:
            prevK = b[k-1]
        idx = range(max(prevK, 0), b[k])
        
        if csize[k] > 1:
            mean = np.zeros(csize[k])
            cov = Bstar[np.ix_(idx, idx)]
            samples = multivariate_normal(mean, cov).rvs(size=n).T
            W[idx, :] = samples
        elif csize[k] == 1:
            mean = 0
            sd = np.sqrt(Bstar[np.ix_(idx, idx)])
            samples = np.random.normal(mean, sd, size=(1, n))
            W[idx, :] = samples

    np.fill_diagonal(amat, 0)
    
    return np.linalg.solve(Bstar, W).T