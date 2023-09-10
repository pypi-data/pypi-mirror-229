import numpy as np

def rmultinom_cg(n, amat, distn):
    vset = [i for i in range(len(amat))]
    p = len(vset)
    data = np.full((n, p), np.nan)
    n_c = len(distn)

    for i in range(n_c):
        temp = distn[i]
        v_idx = temp["Vidx"]
        if temp["cond.dist"].shape[1] > 1:
            b_idx = temp["Bidx"]
            if len(b_idx) > 1:

                config = np.apply_along_axis(
                    lambda x: np.where(np.apply_along_axis(lambda y: np.array_equal(x, y), 1, temp["Btable"]))[0], 
                    1, 
                    data[:, b_idx]
                )
            else:
                config = np.apply_along_axis(
                    lambda x: np.where(np.apply_along_axis(lambda y: y == x, 1, temp["Btable"]))[0], 
                    1, 
                    data[:, b_idx]
                )

            row = np.apply_along_axis(
                lambda x: np.random.choice(np.arange(temp["Vtable"].shape[0]), size=1, p=temp["cond.dist"][:, x].flatten())[0],
                1,
                config
            )
            data[:, v_idx] = temp["Vtable"][row]

        else:
            config = np.random.choice(
                np.arange(temp["Vtable"].shape[0]), 
                size=n, 
                replace=True, 
                p=temp["cond.dist"][:, 0]
            )
            data[:, v_idx] = temp["Vtable"][config]
    return data