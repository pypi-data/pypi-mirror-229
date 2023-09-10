import numpy as np
import igraph as ig

def is_acyclic(adj_matrix):
    n = len(adj_matrix)
    visited = [False] * n
    stack = [False] * n

    def dfs(node):
        visited[node] = True
        stack[node] = True

        for neighbor in range(n):
            if adj_matrix[node][neighbor] == 1:
                if not visited[neighbor]:
                    if dfs(neighbor):
                        return True
                elif stack[neighbor]:
                    return True

        stack[node] = False
        return False

    for node in range(n):
        if not visited[node]:
            if dfs(node):
                return False

    return True

def top_order(adj_matrix):
    n = len(adj_matrix)
    visited = [False] * n
    stack = [False] * n
    topological_order = []

    def dfs(node):
        visited[node] = True
        stack[node] = True

        for neighbor in range(n):
            if adj_matrix[node][neighbor] == 1:
                if not visited[neighbor]:
                    dfs(neighbor)
                elif stack[neighbor]:
                    raise ValueError("The graph is cyclic")

        stack[node] = False
        topological_order.append(node)

    #for node in range(n):
    for node in np.flip(range(n)):
        if not visited[node]:
            dfs(node)

    return topological_order[::-1]

def is_chain_graph(amat):
    wmat = np.matrix((amat + np.transpose(amat)) > 1, dtype=int)
    wg = ig.Graph.Adjacency(wmat.tolist(), mode="undirected")
    cc = wg.connected_components()
    neworder = np.argsort(cc.membership)
    a = np.zeros((len(cc.sizes()), len(cc.sizes())), dtype=int)
    b = np.cumsum(cc.sizes())
    wmat = amat[neworder, :][:, neworder]
    for i in range(len(cc.sizes())):
        for j in range(len(cc.sizes())):
            if j != i:
                if i == 0:
                    prevI = 0
                else:
                    prevI = b[i-1]
                if j == 0:
                    prevJ = 0
                else:
                    prevJ = b[j-1]
                r = range((max(prevI, 0)), b[i])
                c = range((max(prevJ, 0)), b[j])
                a[i, j] = int(np.sum(wmat[np.ix_(r, c)]) > 0)
    output = is_acyclic(a)

    for i in range(len(b)):
        if i == 0:
            prevI = 0
        else:
            prevI = b[i-1]
        r = range((max(prevI, 0)), b[i])
        temp = wmat[np.ix_(r, r)]
        if not np.all(temp == np.transpose(temp)):
            output = False
            break

    vertorder = []
    chainsize = []

    if output:
        chainorder = top_order(a)
        for k in range(len(b)):
            vertorder.extend(np.where(np.array(cc.membership) == chainorder[k])[0])
            chainsize.append(cc.sizes()[chainorder[k]])

    return {"result": output, "vert_order": vertorder, "chain_size": chainsize}