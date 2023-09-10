import numpy as np
import random

"""
This function coverts a graph into triangulated graph.
For this purpose it use One Step Look Ahead Triangulation algorithm

The details of the algorithm can be found at -
Cowell, R. G., Dawid, A. P., Lauritzen, S. L. and Spiegelhalter, D. J. (1999) Probabilistic Networks
and Expert Systems. Springer-Verlag, New York.
"""
def triangulate(adj_matrix):
    k = adj_matrix.shape[0]
    unlabledVertices = np.ones(k, dtype=bool)
    numorder = []
    counter = k

    while counter > 0:
        criterionC = list(np.where(unlabledVertices)[0])
        random.shuffle(criterionC)
        minToFill = k ** 2
        toLabel = k + 1
        neighbors = []
        numNeighbors = 0

        for j in range(counter):
            cUnnumberedNeighbors = np.where((adj_matrix[criterionC[j], :] == 1) & unlabledVertices)[0]
            cUnnumberedNeighbors = np.union1d(cUnnumberedNeighbors, criterionC[j])
            numCUnnumberedNeighbors = len(cUnnumberedNeighbors)
            toFill = numCUnnumberedNeighbors * (numCUnnumberedNeighbors - 1) / 2 - np.sum(adj_matrix[cUnnumberedNeighbors, :][:, cUnnumberedNeighbors]) / 2

            if toFill < minToFill:
                toLabel = criterionC[j]
                neighbors = cUnnumberedNeighbors
                minToFill = toFill
                numNeighbors = numCUnnumberedNeighbors

        if numNeighbors > 0 and minToFill > 0:
            newMatrix = np.ones((numNeighbors, numNeighbors), dtype=int)
            np.fill_diagonal(newMatrix, 0)
            
            for i, valX in enumerate(neighbors):
                for j, valY in enumerate(neighbors):
                    adj_matrix[valX][valY] = newMatrix[i][j]

        numorder.append(toLabel)
        unlabledVertices[toLabel] = False
        counter -= 1

    return adj_matrix