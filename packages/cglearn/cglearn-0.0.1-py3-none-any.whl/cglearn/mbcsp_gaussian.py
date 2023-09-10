import numpy as np
from .norm_ci_test import gaussCItest
from itertools import combinations

# this functions stores column idx in sepset and adj instead of column name itself, unlike R version
def mbcsp_gaussian(dataset, alpha=0.05, maxSx = -1):
    if maxSx == -1:
        maxSx = len(dataset[0])
    corr = np.corrcoef(dataset, rowvar=False)
    columns = [i for i in range(len(dataset[0]))]
    cov = np.cov(dataset, rowvar=False, bias=True)
    d = np.sqrt(cov.diagonal())
    parcor = ((cov.T/d).T)/d
    n = len(dataset)
    suffStat = {'C' : parcor, 'n' : n}

    # Helper function to compute adjacencies
    def adjecencies(dataset, alpha):

        def findMinPVal(v, T, cond, k):
            maxpVal = float('-inf')
            sepSet = []
            def find_subsets():
                return list(combinations(cond, k))
            sets = find_subsets()

            for s in sets:
                S = list(s)
                pval = gaussCItest(v, T, S, suffStat)
                if pval > alpha:
                    maxpVal = pval
                    sepSet = S
                    return {'p_val':maxpVal, 'sepSet':sepSet}

            return {'p_val':maxpVal, 'sepSet':sepSet}

        sepset = {col: {col2: [] for col2 in columns} for col in columns}
        adjs = {col: [] for col in columns}
        for T in columns:
            S = []
            adjT = []
            diffSet = set(columns) - set([T])
            for v in diffSet:
                p_val = gaussCItest(v, T, S, suffStat)
                if p_val > alpha:
                    sepset[T][v] = S
                else:
                    adjT.append(v)

            k = 1
            sorted_indices = sorted(range(len(corr[adjT, T])), key=lambda k: corr[adjT, T][k])
            sorted_adj = [adjT[i] for i in sorted_indices]
            nNum = min(len(adjT), maxSx)

            if nNum < 1:
                adjs[T] = []
            else:
                while k <= nNum:
                    sorted_adj_copy = sorted_adj.copy()
                    for v in sorted_adj_copy:
                        condset = [x for x in sorted_adj if x!=v]
                        len_condset = len(condset)
                        if k > len_condset:
                            k = nNum
                            break
                        a = findMinPVal(v, T, condset, k)
                        if a["p_val"] >= alpha:
                            sorted_adj.remove(v)
                            sepset[T][v] = a["sepSet"]
                    k += 1
                    nNum = len(sorted_adj)

                adjs[T] = sorted_adj

        for var in columns:
            for u in adjs[var]:
                if var not in adjs[u]:
                    adjs[var].remove(u)
                    sepset[var][u] = sepset[u][var]

        return {"adjs": adjs, "sepset": sepset}

    # Helper function to find Markov Blanket for a target variable T
    def find_mb(T, adjs, sepset, alpha):
        adjT = adjs[T]
        mmbT = set(adjT)

        candids = set(columns) - set([T]) - set(adjT)

        for ch in adjT:
            for csp in candids:
                l1 = sepset[T][csp]
                pval1 = gaussCItest(csp, T, l1, suffStat)
                l1.append(ch)
                pval2 = gaussCItest(csp, T, l1, suffStat)
                if abs(pval1) > alpha and abs(pval2) <= alpha:
                    mmbT.add(csp)
        
        
        continue_shrinking = True
        del_cand = list(mmbT)
        
        if len(del_cand) == 0:
            continue_shrinking = False

        while continue_shrinking:
            p_vals = [gaussCItest(T, x, list(set(mmbT) - set([x])), suffStat) for x in del_cand]
            p_val_max = max(p_vals)
            idx = p_vals.index(p_val_max)
        
            if p_val_max > alpha:
                mmbT.remove(del_cand[idx])
                del_cand.remove(del_cand[idx])
            else:
                continue_shrinking = False
        return list(mmbT)

    # Compute adjacencies and separation sets
    result = adjecencies(dataset, alpha)

    mb = {}
    for i in range(len(dataset[0])):
        mb[i] = find_mb(i, result["adjs"], result["sepset"], 0.05)
    p = len(columns)
    G = np.zeros((p, p))
    G = G.astype(int)

    for var in columns:
        for u in mb[var]:
            if var not in mb[u]:
                mb[var].remove(u)

    for u, vList in mb.items():
        for v in vList:
            G[u][v] = 1
            G[v][u] = 1

    return G
