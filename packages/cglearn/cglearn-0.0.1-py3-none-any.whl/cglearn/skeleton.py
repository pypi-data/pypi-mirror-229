import numpy as np

# this function returns skeleton of a chain graph
# amat - adjecancy matrix
def skeleton(amat):
    return np.maximum(amat, amat.T)
