import numpy as np
from .junctiontree import SepPair
from .norm_ci_test import gaussCItest

# This function is used to get the next probable separation set to check the d-separation between two vertices
# (for details, check gaussian_pc_learn) 
# n : length of neighbors
# k : set size
# S : separation set
def get_next_set(n, k, S):
    result = [x - y for x, y in zip(list(range(n - k, n)), S)]
    zeros = result.count(0)
    chInd = k - zeros
    
    wasLast = (chInd == 0)
    if not wasLast:
        S[chInd - 1] += 1
        if chInd < k:
            S[chInd:k+1] = list(range(S[chInd - 1] + 1, S[chInd - 1] + zeros + 1))
            
    return {'nextSet': S, 'wasLast': wasLast}

# The following procedure (Spirtes, Glymour, and Scheines 1991) starts by forming the complete undirected graph,
# then “thins” that graph by removing edges with zero order conditional independence
# relations, thins again with first order conditional independence relations, and so on.
def gaussian_pc_learn(cov, n, p_value, algMethod = "original", vertexNames = []):
    p = cov.shape[0]
    if len(vertexNames) == 0:
        vset = [i for i in range(p)]
    else:
        vset = vertexNames
    sep_pairs = []
    G = np.full((p, p), True)
    np.fill_diagonal(G, False)
    seq_p = np.arange(0, p)
    done = False
    ord_val = 0

    while not done and np.any(G):
        done = True
        ind = np.argwhere(G)
        ind = ind[np.lexsort((ind[:, 1], ind[:, 0]))]
        remaining_edge_tests = ind.shape[0]

        # cov to cor
        d = np.sqrt(cov.diagonal())
        parcor = ((cov.T/d).T)/d
        
        # need to add this to gaussCItest
        stuffStat = {'C' : parcor, 'n' : n}

        if algMethod == "stable":
            G_stable = G.copy()

        for i in range(remaining_edge_tests):
            x = ind[i, 0]
            y = ind[i, 1]
            if G[y, x]:
                nbrs_bool = G[:, x].copy() if algMethod != "stable" else G_stable[:, x].copy()
                nbrs_bool[y] = False
                nbrs = seq_p[nbrs_bool]
                length_nbrs = len(nbrs)
                if length_nbrs >= ord_val:
                    if length_nbrs > ord_val:
                        done = False
                    S = [i for i in range(ord_val)]
                    while True:
                        # here we must pass index and not the actual coluname as gaussCItest needs index
                        p_val = gaussCItest(x, y, [int(nbrs[ptr]) for ptr in S], stuffStat)
                        if p_val > p_value:
                            G[x, y] = G[y, x] = False
                            # add vertex u, vertex v and separation set S for d-separation
                            pair = SepPair(u=vset[x], v=  vset[y], s = [vset[int(nbrs[ptr])] for ptr in S], vertexNames = vertexNames)
                            sep_pairs.append(pair)
                            break
                        else:
                            # get next possible separation set
                            next_set = get_next_set(length_nbrs, ord_val, S)
                            if next_set["wasLast"]:
                                break
                            S = next_set["nextSet"]
        ord_val += 1
    amat = G.astype(int)
    amat = [[int(G) for G in row] for row in amat]
    amat = np.array(amat)
    return {"amat": amat, "sep_pairs": sep_pairs}