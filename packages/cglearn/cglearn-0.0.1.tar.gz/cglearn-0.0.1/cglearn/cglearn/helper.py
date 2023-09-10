import numpy as np
# This function creates junction tree from the given information on cliques
# c - stores the information on cliques and separator
# vset - vertex names
def junc_tree(c, vset):

    n = c["n.clique"]
    clique = [dict() for _ in range(n)]
    cnames = ["C" + str(i) for i in range(1, n+1)]

    for i in range(n):
        clique[i]["name"] = cnames[i]
        clique[i]["vset"] = [vset[j] for j in c["cliques"][i]]

    adjmat = np.zeros((n, n), dtype=int)
    np.fill_diagonal(adjmat, 0)
    sep = []
    temp = []
    k = 0

    if n > 1:
        for i in range(1, n):
            temp.extend(clique[i - 1]['vset'])
            test = np.intersect1d(clique[i]['vset'], temp)
            
            for j in range(i):
                if np.all(np.isin(test, clique[j]['vset'])):
                    adjmat[i, j] = 1
                    sep.append({'separator': np.intersect1d(clique[j]['vset'], clique[i]['vset']),
                                'edge': ['C' + str(j+1), 'C' + str(i+1)]})
                    k += 1
                    break
    
    adjmat += adjmat.T

    return {'tree.struct': adjmat, 'cliques': clique, 'separators': sep}


# This function finds all the cliques in the given triangulated graph
def find_clique(input):
    if not input["is.triangulated"]:
        raise ValueError("Invalid Input!")

    n = input["perfect.numbering"]
    card = input["card"]
    rcd = input["pi.record"]
    lad = []
    kep = []
    for i in range(len(n)):
        if i == len(n) - 1 or (card[i] + 1) > card[i + 1]:
            lad.append(n[i])
            kep.append(i)

    clique = []
    for j in range(len(lad)):
        if card[kep[j]] > 0:
            a = sum(card[0:kep[j]])
            clique.append([lad[j]] + list(rcd[a:a+card[kep[j]]]))
        else:
            clique.append([lad[j]])

    return {
        "n.clique": len(lad),
        "cliques": clique
    }