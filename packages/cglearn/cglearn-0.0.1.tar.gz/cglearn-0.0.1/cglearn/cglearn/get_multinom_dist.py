import numpy as np
from .is_chain_graph import is_chain_graph
import igraph as ig

def cliques(amat, VB):
    vertices = VB
    amat_graph = ig.Graph.Adjacency(amat.tolist(), mode=ig.ADJ_MAX)
    cliq_list = amat_graph.cliques()
    return [[vertices[k] for k in x] for x in cliq_list]

def get_parents(V, amat):
    parents = set()
    num_vertices = len(V)
    
    for i in range(len(amat)):
        for j in range(num_vertices):
            if amat[i][V[j]] == 1 and amat[V[j]][i] == 0:
                parents.add(i)
    
    return parents

def make_table(n_state, subset, alpha, beta, freq=True):
    idx = subset
    phi = np.zeros((np.prod([n_state[i] for i in idx]), len(idx)))
    
    for k in range(len(idx)):
        a = n_state[idx[k]]
        b = np.prod([n_state[i] for i in idx[k+1:]]) if k != len(idx)-1 else 1
        c = np.prod([n_state[i] for i in idx[:k]]) if k != 0 else 1
        phi[:, k] = np.tile(np.repeat(np.arange(1, a+1), np.repeat(b, a)), c)
    if freq:
        n = phi.shape[0]
        Freq = np.random.beta(alpha, beta, size=n)
        phi = np.column_stack((phi, Freq))
    return phi


def get_multinom_dist(amat, n_state, alpha = 1, beta = 1):
    output = is_chain_graph(amat)
    if not output['result']:
        raise ValueError("The input should be a chain graph!")
    
    p = amat.shape[0]
    corder = output["vert_order"]
    csize = output["chain_size"]
    b = np.cumsum(csize)
    n_c = len(csize)
    distn = [None] * n_c
    for i in range(n_c):
        r = range((0 if i == 0 else b[i-1]), b[i])
        V = [corder[k] for k in r]
        B = get_parents(V, amat)
        VB = list(B) + V
        Kstar = amat[np.ix_(VB, VB)]
        if len(B) != 0:
            idxB = [k for k, elem in enumerate(VB) if elem in B]
            Kstar[np.ix_(idxB, idxB)] = 1
            np.fill_diagonal(Kstar, 0)
        if Kstar.shape[0] == 1:
            A = [V]
        else:
            A = cliques(Kstar, VB)
        pot = [None] * len(A)
        for j in range(len(A)):
            # Specify potential for each clique in K*(t)
            pot[j] = make_table(n_state, A[j], alpha, beta, True)

        if len(B) == 0:
            Btable = np.full((1, 1), np.nan)
        else:
            Btable = make_table(n_state, list(B), alpha, beta, False)

        Vtable = make_table(n_state, V, alpha, beta, False)
        cond_dist = np.zeros((Vtable.shape[0], Btable.shape[0]))
        for k in range(Btable.shape[0]):
            for l in range(Vtable.shape[0]):
                config = np.concatenate((Btable[k, :], Vtable[l, :]))
                config = config[~np.isnan(config)]
                vert = list(B) + V
                m = 1
                for r in range(len(pot)):
                    test = config[np.where(np.isin(vert, A[r]))[0]]
                    row = np.apply_along_axis(lambda x: np.all(x[:-1] == test), 1, pot[r])
                    m *= np.prod(pot[r][row, -1])
                cond_dist[l, k] = m
        cond_dist = cond_dist / np.sum(cond_dist, axis=0)
        distn[i] ={"Btable": Btable, "Bidx":list(B), "Vtable": Vtable, "Vidx":V, "cond.dist": cond_dist}
    return distn