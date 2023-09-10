import numpy as np
from .multinom_pc_learn import multinom_pc_learn, get_next_set
from .junctiontree import SepTree, SepPair
from .multinom_ci_test import multinom_ci_test
from .compress_freq_table import compress_freq_tb

# learns the skeleton from the junction tree
# tree: A SepTree object representing the tree structure
# cov: A covariance matrix.
# n: An integer specifying the sample size.
# p_value: A significance level used in statistical tests.
# drop: A boolean 
def learn_skeleton_multinom(tree:SepTree, freq_tb, p_value, drop=True):
    # Function to get candidate pairs for separating variables
    def get_exed_cand(tree, amat):
        n_clique = len(tree.cliques)
        cand_pairs = []
        if n_clique == 1:
            return cand_pairs
        for i in range(n_clique - 1):
            sepset = tree.separators[i]["separator"]
            idx = [int(i) for i in sepset]
            G = amat[np.ix_(idx, idx)]
            ind = list(zip(*np.where(G == 1)))
            if ind:
                for row, col in ind:
                    cand_pairs.append([idx[row], idx[col]])
        return cand_pairs

    vnames = freq_tb.colnames[:-1]
    local_ug = []
    n_clique = len(tree.cliques)
    
    # Learn local undirected graphs within cliques
    for i in range(n_clique):
        idx = tree.cliques[i]["vset"]
        idx = [int(num) for num in idx]
        new_freq_tb = compress_freq_tb(freq_tb, idx)
        new_ug = multinom_pc_learn(new_freq_tb, p_value, idx)
        local_ug.append(new_ug)
    
    p = len(vnames)
    amat = np.zeros((p, p), dtype=int)
    for i in range(n_clique):
        idx = tree.cliques[i]["vset"]
        idx = [int(num) for num in idx]
        amat[np.ix_(idx, idx)] = 1

    np.fill_diagonal(amat, 0)
    sep_pairs = []
    n_loc_sep = len(local_ug)

    if n_loc_sep > 0:
        for i in range(n_loc_sep):
            for j in range(len((local_ug[i])["sep_pairs"])):
                u = (local_ug[i])["sep_pairs"][j].u
                v = (local_ug[i])["sep_pairs"][j].v
                if amat[u, v] == 1:
                    amat[u, v] = amat[v, u] = 0
                    sep_pairs.append((local_ug[i])["sep_pairs"][j])

    if drop:
        ind = get_exed_cand(tree, amat)
        if ind:
            # sort indices by row, col
            ind = sorted(ind, key=lambda x: (x[0]))
            seq_p = np.arange(0, p)
            done = False
            ord_val = 0
            remaining_edge_tests = len(ind)#ind.shape[0]
            while not done and np.any(amat.astype(bool)):
                done = True
                for i in range(remaining_edge_tests):
                    x = ind[i][0]
                    y = ind[i][1]
                    if amat[y, x]:
                        nbrs_bool = amat[:, x].copy()
                        nbrs_bool[y] = False
                        nbrs = [idx for idx in seq_p if nbrs_bool[idx]==1]
                        length_nbrs = len(nbrs)
                        if length_nbrs >= ord_val:
                            if length_nbrs > ord_val:
                                done = False
                            S = [i for i in range(ord_val)]
                            while True:
                                p_val = multinom_ci_test(freq_tb, vnames[x], vnames[y], [vnames[nbrs[ptr]] for ptr in S])['pval']
                                if p_val > p_value:
                                    amat[x, y] = amat[y, x] = False
                                    pair = SepPair(u= vnames[x], v= vnames[y], s = [vnames[nbrs[ptr]] for ptr in S])
                                    sep_pairs.append(pair)
                                    break
                                else:
                                    next_set = get_next_set(length_nbrs, ord_val, S)
                                    if next_set["wasLast"]:
                                        break
                                    S = next_set["nextSet"]
                ord_val += 1



    return {"amat": amat, "sep_pairs": sep_pairs}