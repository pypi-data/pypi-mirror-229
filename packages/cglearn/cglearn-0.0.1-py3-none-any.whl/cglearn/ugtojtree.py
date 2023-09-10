from .istriangulated import is_triangulated
from .triangulate import triangulate
from .helper import find_clique, junc_tree
from .junctiontree import SepTree

"""
This function coverts an undirected graph into junction tree
adj_matrix - This is the adjacency matrix of the undirected graph
Returns SepTree object
"""
def ug_to_jtree(adj_matrix):
    output = is_triangulated(triangulate(adj_matrix))
    num_rows = adj_matrix.shape[0]
    vset = [str(i) for i in range(num_rows)]
    tree = junc_tree(find_clique(output), vset)
    return SepTree(tree["tree.struct"],tree["cliques"],tree["separators"])