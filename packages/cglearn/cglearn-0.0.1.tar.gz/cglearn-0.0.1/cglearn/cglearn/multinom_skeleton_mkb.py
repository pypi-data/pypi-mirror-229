import numpy as np
from .multinom_pc_learn import get_next_set
from .junctiontree import  SepPair
from .multinom_ci_test import multinom_ci_test
from .uig_multinom import naive_getug_multinom
from .mbcsp_discrete import mbcsp_discrete

def multinom_skeleton_mkb(freq_tb, p_value, ds, method="original"):
    vnames = freq_tb.colnames[:-1]
    p = len(vnames)
    sep_pairs = []

    # Phase 1: Learning Markov blankets
    if method == "original":
        G = naive_getug_multinom(freq_tb, p_value, "mkb")
    else:
        G = mbcsp_discrete(ds, p_value)
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
                        p_val = multinom_ci_test(freq_tb, x, y, [nbrs[ptr] for ptr in S])['pval']
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