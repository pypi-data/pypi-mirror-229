# This class maintains the junction tree
# tree.struct - structure of junction tree
# cliques"  - information on cliques
# separators - information on node separators
class SepTree:
    def __init__(self, tree_struct, cliques, separators):
        self.tree_struct = tree_struct
        self.cliques = cliques
        self.separators = separators

# This class maintains the separation pairs
# u - vertex 1
# v - vertex 2
# s - separating set for vertex 1 & 2

# NEED TO DELETE THIS AND THINK OF A BETTER APPROACH 
# vertexName - column names that is actually used for understaning the matrix for gaussian_pc_learn in learn_skeleton_norm(line 35), we pass subset of cov and not whole cov, hence need to know the vertexNames passed
class SepPair:
    def __init__(self, u, v, s, vertexNames = []):
        self.u = u
        self.v = v
        self.s = s
        self.vertexNamee = vertexNames