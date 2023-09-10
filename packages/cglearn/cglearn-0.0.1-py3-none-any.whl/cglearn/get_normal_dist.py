import numpy as np
from .is_chain_graph import is_chain_graph

def get_normal_dist(amat):
    output = is_chain_graph(amat)
    if not output['result']:
        raise ValueError("The input should be a chain graph!")
    
    p = amat.shape[0]
    corder = np.flip(output["vert_order"])
    csize = np.flip(output["chain_size"])
    b = np.cumsum(csize)

    if p > 1:
        amat = amat[corder, :][:, corder]

    Bstar = np.zeros((p, p))
    admissible = False
    niter = 0
    
    # # repeat till we get the block diagonal of Bstar all pos-def!
    while not admissible:
        admissible = True
        niter += 1
        for k in range(len(csize)):
            if k == 0:
                prevK = 0
            else:
                prevK = b[k - 1]
            aa = p - max(prevK, 0)
            bb = b[k] - max(prevK, 0)
            randdist = np.random.uniform(0.5/bb, 1.5/bb, size=(aa, aa)) * np.random.choice([-1, 1], size=(aa, aa), replace=True)
            np.set_printoptions(precision=2, suppress=True)
            randdist[np.triu_indices(aa)] = randdist.T[np.triu_indices(aa)]
            np.fill_diagonal(randdist, 1)

            if k == 0:
                prevI = 0
            else:
                prevI = b[k-1]
            r = range((max(prevI, 0)), p)
            Bstar[np.ix_(r, r)] = randdist
            
            # Bstar[max(b[k - 1], 0):p, max(b[k - 1], 0):p] = randdist
            
            if k != len(csize) - 1:
                if k == 0:
                    prevK = 0
                else:
                    prevK = b[k-1]
                Bstar[b[k]:p, max(prevK, 0):b[k]] = 0
        
        np.fill_diagonal(amat, 1)
        Bstar = Bstar * amat.T
        
        for k in range(len(csize)):
            if k == 0:
                prevK = 0
            else:
                prevK = b[k-1]
            r = range(max(prevK, 0), b[k])
            if not np.all(Bstar[np.ix_(r, r)] == Bstar[np.ix_(r, r)].T):
                print("Block diagonal not symmetric!")
            
            if len(r) > 1 and np.linalg.eigvalsh(Bstar[np.ix_(r, r)])[-1] < 0:
                admissible = False
                break
    
    return {"Bstar":Bstar, "corder":corder} # return corder as rownames and colnames
