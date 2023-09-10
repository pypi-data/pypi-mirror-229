from .graph import Graph

# this function find the ancestral set of given set of vertices(setA) in the given graph
def find_ancestral_set(setA : set, graph : Graph)->set:
    
    # this is a hrlper function which recursively adds neighbors and parents of unvisited vertices
    def add_neighbors_parents(v):
        ancestralSet.add(v)
        parents = graph.get_parents(v)
        neighbors = set(graph.get_neighbors(v))
        parentsAndNeighbors = parents.union(neighbors)

        for nbr in parentsAndNeighbors:
            if nbr not in ancestralSet:
                add_neighbors_parents(nbr)

    ancestralSet = set()
    for vertex in setA:
        if vertex not in ancestralSet:
            add_neighbors_parents(vertex)
    return ancestralSet