import random

"""
This function check if the given graph is triangulated or not.
For this purpose it use maximum cardinality search algorithm

The details of the algorithm can be found at -
Tarjan, R. E. and Yannakakis, M. (1984). Simple linear-time algorithms to test chordality of graphs,
test acyclicity of hypergraphs, and selectively reduce acyclic hypergraphs. SIAM Journal on Computing, 13, 566-79.
"""
def is_triangulated(adj_matrix):
    output = True
    k = len(adj_matrix)
    numbering = []
    vertices = list(range(0, k))
    C = [0] * k
    card = []
    pi_record = []
    
    for j in range(1, k + 1):
        U = list(set(vertices) - set(numbering))
        maxInC = max([C[u] for u in U])
        pos = []
        for i, val in enumerate(U):
            if C[val] == maxInC:
                pos.append(i)

        if len(pos) > 1:
            v = U[random.choice(pos)]
        else:
            v = U[pos[0]]
        
        neighborsV = [i for i, val in enumerate(adj_matrix[v]) if val == 1]
        pi_v = list(set(neighborsV).intersection(numbering))
        m = len(pi_v)
        card.append(m)
        pi_record.extend(pi_v)
        
        numEdges = sum([adj_matrix[i][j] for i in pi_v for j in pi_v]) / 2
        if numEdges < m * (m - 1) / 2:
            output = False
            break
        
        neighborsU = list(set(neighborsV).intersection(U))
        
        for u in neighborsU:
            C[u] += 1
        
        numbering.append(v)
    
    return {
        "is.triangulated": output,
        "perfect.numbering": numbering,
        "card": card,
        "pi.record": pi_record
    }