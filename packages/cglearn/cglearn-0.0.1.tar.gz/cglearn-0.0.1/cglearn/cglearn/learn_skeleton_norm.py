import numpy as np
from .gaussianpclearn import gaussian_pc_learn, get_next_set
from .junctiontree import SepTree, SepPair
from .norm_ci_test import gaussCItest

# learns the skeleton from the junction tree
# tree: A SepTree object representing the tree structure
# cov: A covariance matrix.
# n: An integer specifying the sample size.
# p_value: A significance level used in statistical tests.
# drop: A boolean 
def learn_skeleton_norm(tree:SepTree, cov, n, p_value, drop=True):
    
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
                # ind = [[idx[row], idx[col]] for row, col in ind]
                # cand_pairs.append(ind)
                for row, col in ind:
                    cand_pairs.append([idx[row], idx[col]])
        return cand_pairs


    vset = len(cov)
    local_ug = []
    n_clique = len(tree.cliques)
    
    # Learn local undirected graphs within cliques
    for i in range(n_clique):
        idx = tree.cliques[i]["vset"]
        idx = [int(num) for num in idx]
        covMat = cov[np.ix_(idx, idx)]
        new_ug = gaussian_pc_learn(covMat, n, p_value, idx)
        if len(new_ug["sep_pairs"]) > 0:
            # for i in range(len(new_ug["sep_pairs"])):
            #     new_ug["sep_pairs"][i].u = idx[int(new_ug["sep_pairs"][i].u)]
            #     new_ug["sep_pairs"][i].v = idx[int(new_ug["sep_pairs"][i].v)]
            #     for j in range(len(new_ug["sep_pairs"][i].s)):
            #         new_ug["sep_pairs"][i].s[j] = idx[int(new_ug["sep_pairs"][i].s[j])]
            local_ug.append(new_ug)
    
    p = vset
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
            ind = sorted(ind, key=lambda x: (x[0], x[1]))
            seq_p = np.arange(0, p)
            done = False
            ord_val = 0
            remaining_edge_tests = len(ind) #ind.shape[0]

            d = np.sqrt(cov.diagonal())
            parcor = ((cov.T/d).T)/d
            
            stuffStat = {'C' : parcor, 'n' : n}
            while not done and np.any(amat.astype(bool)):
                done = True
                for i in range(remaining_edge_tests):
                    x = ind[i][0]
                    y = ind[i][1]
                    if amat[y, x]:
                        nbrs_bool = amat[:, x].copy()
                        nbrs_bool[y] = False
                        # nbrs = seq_p[nbrs_bool]
                        nbrs = [idx for idx in seq_p if nbrs_bool[idx]==1]
                        length_nbrs = len(nbrs)
                        if length_nbrs >= ord_val:
                            if length_nbrs > ord_val:
                                done = False
                            S = [i for i in range(ord_val)]
                            while True:
                                p_val = gaussCItest(x, y, [nbrs[ptr] for ptr in S], stuffStat)
                                if p_val > p_value:
                                    amat[x, y] = amat[y, x] = False
                                    pair = SepPair(u=x, v=y, s = [j for j in [nbrs[ptr] for ptr in S]])
                                    sep_pairs.append(pair)
                                    break
                                else:
                                    next_set = get_next_set(length_nbrs, ord_val, S)
                                    if next_set["wasLast"]:
                                        break
                                    S = next_set["nextSet"]
                ord_val += 1



    return {"amat": amat, "sep_pairs": sep_pairs}