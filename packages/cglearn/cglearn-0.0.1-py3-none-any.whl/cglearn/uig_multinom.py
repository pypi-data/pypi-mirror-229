import numpy as np
from .multinom_ci_test import multinom_ci_test
from .skeleton import skeleton
from .compress_freq_table import compress_freq_tb
import pandas as pd

def learn_mkvblkt(freq_tb, var, curr=[], p_value = 0.05):
    forbid = curr.copy()
    vnames = freq_tb.colnames[:-1]
    rest = list(set(vnames) - set(np.append(curr, var)))
    continue_grow = True

    # Grow phase
    while continue_grow:
        p_vals = [multinom_ci_test(freq_tb, var, x, curr)['pval'] for x in rest]

        # Need to add this, not in LCD
        if p_vals == []:
            break
        # 

        p_val_min = min(p_vals)
        idx = p_vals.index(p_val_min)
        if p_val_min < p_value:
            curr.append(rest[idx])
            rest.pop(idx)
        else:
            continue_grow = False
    
    continue_shrink = True
    # freq_tb = compress_freq_tb(freq_tb, curr.append(var))
    freq_tb = compress_freq_tb(freq_tb, curr +[var])
    del_cand = list(set(curr) - set(forbid))
    
    if len(del_cand) == 0:
        continue_shrink = False
    
    # Shrink phase
    while continue_shrink:
        p_vals = [multinom_ci_test(freq_tb, var, x, list(set(curr) - set([x])))['pval'] for x in del_cand]
        p_val_max = max(p_vals)
        idx = p_vals.index(p_val_max)
        
        if p_val_max > p_value:
            curr = list(set(curr) - set([del_cand[idx]]))
            del_cand.pop(idx)
        else:
            continue_shrink = False
    
    return curr

def naive_getug_mkb(freq_tb, p_value):
    vnames = freq_tb.colnames[:-1]
    p = len(vnames)
    amat = np.zeros((p, p))
    vset = np.random.permutation(vnames)

    p = len(vset)
    amat = pd.DataFrame(0, index=vset, columns=vset, dtype=int)

    for i in range(p):
        curr = [vset[j] for j in np.where(amat.loc[vset[i], :] == 1)[0]]
        res = learn_mkvblkt(freq_tb, vset[i], curr, p_value)
        # Set the values to 1 using row names and column names
        amat.loc[vset[i], res] = 1
        amat.loc[res, vset[i]] = 1

    amat = amat.reindex(index=vnames, columns=vnames)
    return amat.values

def naive_getug_multinom(freq_tb, p_value, method="mkb"):
    mm = 1 if method == "mkb" else 2 if method == "simple" else 3 if method == "fwd" else 0
    if mm == 0:
        raise ValueError("Invalid method!")
    
    vnames = freq_tb.colnames[:-1]
    p = len(vnames)
    amat = np.zeros((p, p))
    amat = amat.astype(int)
    
    if mm == 1:
        pass
        return naive_getug_mkb(freq_tb, p_value)
    elif mm == 2:
        for i in range(p-1):
            for j in range(i+1, p):
                pval = multinom_ci_test(freq_tb, vnames[i], vnames[j], [vnames[k] for k in range(p) if k!=i and k!=j])["pval"]
                amat[i, j] = pval < p_value
        return skeleton(amat)
    return amat