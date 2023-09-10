from .graph import Graph
import numpy as np

# this function generates induced subgraph given a list of vertices in a given graph
def find_induced_subgraph(vertices : list, graph : Graph):
    num_nodes = len(graph.adjacency_matrix)
    inducedSubgraph = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]
    inducedSubgraph = np.array(inducedSubgraph)

    # note that we are not visited all rows and column of the matrix
    # we visit only vertices which are required for induced subgraph
    for i in vertices:
        for j in vertices:
            inducedSubgraph[i][j] = graph.adjacency_matrix[i][j]

    return inducedSubgraph