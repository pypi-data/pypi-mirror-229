import numpy as np
from .gaussianpclearn import get_next_set
from .junctiontree import  SepPair
from .norm_ci_test import gaussCItest
import pandas as pd
from .mbcsp_gaussian import mbcsp_gaussian

# Learns the Markov blanket of a target variable using conditional independence tests.
# Arguments:
#   - cov: Covariance matrix of the variables.
#   - n: Number of sample cases (number of rows in the data).
#   - var: Index of the target variable.
#   - curr: List of variables included
#   - p_value: Threshold p-value for conditional independence tests (optional, default = 0.05).
# Returns:
#   - curr: List of variables in the Markov blanket of the target variable.
def gaussian_learn_mkvblkt(cov, n, var, curr=[], p_value = 0.05):
    # cov: covariance matrix
    # n: number of sample cases (# of rows in data)
    forbid = curr.copy()
    vnames = list(range(len(cov)))
    vnames = vnames[:-1]
    rest = list(set(vnames) - set(np.append(curr, var)))
    continue_grow = True
    
    d = np.sqrt(cov.diagonal())
    parcor = ((cov.T/d).T)/d
    stuffStat = {'C' : parcor, 'n' : n}

    # Grow phase
    while continue_grow:
        p_vals = [gaussCItest(var, x, curr, stuffStat) for x in rest]
        p_val_min = min(p_vals)
        idx = p_vals.index(p_val_min)
        if p_val_min < p_value:
            curr.append(rest[idx])
            rest.pop(idx)
        else:
            continue_grow = False
    
    continue_shrink = True
    del_cand = list(set(curr) - set(forbid))
    
    if len(del_cand) == 0:
        continue_shrink = False
    
    # Shrink phase
    while continue_shrink:
        p_vals = [gaussCItest(var, x, list(set(curr) - set([x])), stuffStat) for x in del_cand]
        p_val_max = max(p_vals)
        idx = p_vals.index(p_val_max)
        
        if p_val_max > p_value:
            curr = list(set(curr) - set([del_cand[idx]]))
            del_cand.pop(idx)
        else:
            continue_shrink = False
    
    return curr  # return the Markov blanket of variable "var"


# Constructs an undirected graph by learning the Markov blankets for all variables.
# Arguments:
#   - cov: Covariance matrix of the variables.
#   - n: Number of sample cases (number of rows in the data).
#   - p_value: Threshold p-value for conditional independence tests.
# Returns:
#   - amat: Adjacency matrix of the undirected graph.
def gaussian_uig_mkb(cov, n, p_value):
    vnames = list(range(len(cov)))
    p = len(vnames)
    amat = np.zeros((p, p))
    vset = np.random.permutation(vnames)

    p = len(vset)
    amat = pd.DataFrame(0, index=vset, columns=vset, dtype=int)

    for i in range(p):
        curr = [vset[j] for j in np.where(amat.loc[vset[i], :] == 1)[0]]
        res = gaussian_learn_mkvblkt(cov, n, vset[i], curr, p_value)
        # Set the values to 1 using row names and column names
        amat.loc[vset[i], res] = 1
        amat.loc[res, vset[i]] = 1

    amat = amat.reindex(index=vnames, columns=vnames)
    return amat.values

# Performs skeleton learning by iteratively removing edges based on conditional independence tests.
# Arguments:
#   - cov: Covariance matrix of the variables.
#   - n: Number of sample cases (number of rows in the data).
#   - p_value: Threshold p-value for conditional independence tests.
# Returns:
#   - Dictionary containing the following:
#     - amat: Adjacency matrix of the learned skeleton.
#     - sep_pairs: List of separation pairs indicating the separation sets between variables.
def gaussian_skeleton_mkb(cov, n, p_value, ds, method="original"):
    p = cov.shape[0]
    sep_pairs = []

    # Phase 1: Learning Markov blankets
    if method == "original":
        G = gaussian_uig_mkb(cov, n, p_value) #mbcsp is other option
    else:
        G = mbcsp_gaussian(ds, p_value) #mbcsp is other option
    G = np.asarray(G, dtype=bool)
    
    for i in range(p - 1):
        for j in range(i + 1, p):
            if not G[i, j]:
                neighborsOFi = np.where(G[i, :])[0]  # this is Mb(Xi)
                neighborsOFj = np.where(G[j, :])[0]  # this is Mb(Xj)
                # Set Sepset(Xi, Xj) = Sepset(Xj, Xi) to the smallest of Mb(Xi) and Mb(Xj)
                if len(neighborsOFi) < len(neighborsOFj):
                    pair = SepPair(u=i, v=j, s = [k for k in neighborsOFi])
                    sep_pairs.append(pair)
                else:
                    pair = SepPair(u=i, v=j, s = [k for k in neighborsOFj])
                    sep_pairs.append(pair)

    
    seq_p = np.arange(0, p)
    done = False
    ord_val = 0

    d = np.sqrt(cov.diagonal())
    parcor = ((cov.T/d).T)/d
    
    stuffStat = {'C' : parcor, 'n' : n}

    while not done and np.any(G.astype(bool)):
        done = True
        ind = np.argwhere(G)
        ind = ind[np.lexsort((ind[:, 1], ind[:, 0]))]
        remaining_edge_tests = ind.shape[0]
        for i in range(remaining_edge_tests):
            x = ind[i, 0]
            y = ind[i, 1]
            if G[y, x]:
                nbrs_bool = G[:, x].copy()
                nbrs_bool[y] = False
                nbrs = seq_p[nbrs_bool]
                length_nbrs = len(nbrs)
                if length_nbrs >= ord_val:
                    if length_nbrs > ord_val:
                        done = False
                    S = [i for i in range(ord_val)]
                    while True:
                        p_val = gaussCItest(x, y, [nbrs[ptr] for ptr in S], stuffStat)
                        if p_val > p_value:
                            G[x, y] = G[y, x] = False
                            pair = SepPair(u=x, v=y, s = [j for j in [nbrs[ptr] for ptr in S]])
                            sep_pairs.append(pair)
                            break
                        else:
                            next_set = get_next_set(length_nbrs, ord_val, S)
                            if next_set["wasLast"]:
                                break
                            S = next_set["nextSet"]
        ord_val += 1

    amat = G.astype(int)
    amat = [[int(G) for G in row] for row in amat]
    amat = np.array(amat)
    return {"amat": amat, "sep_pairs": sep_pairs}