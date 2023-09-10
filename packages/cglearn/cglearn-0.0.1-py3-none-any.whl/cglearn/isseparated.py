import numpy as np
from .graph import Graph
from .inducedsubgraph import find_induced_subgraph
from .ancestralset import find_ancestral_set
from .moralize import get_moralize_matrix
from collections import deque

# This function checks if the vertex from setA are C-separated from setB given a separator setC in the given chain graph
# setA              : a set consisting of single or multiple vertices
# setB              : a set consisting of single or multiple vertices
# setSeparator      : a set consisting of zero or multiple vertices
# adjacency_matrix  : adjacency matrix of the chain graph
def is_separated(setA : set, setB : set, setSeparator : set, adjacency_matrix : np.array) -> bool:

    # this function checks if the vertex from setA are connected with setB given a separator setC
    # moralizedMatrix - the graph obtained after moralizing the inducded subgraph of the ancestral set of setA, setB, setSeparator
    def is_connected(setA : set, setB : set, setSeparator : set, moralizedMatrix : np.array) -> bool:

        # applying DFS to check if the path exist to setB from curr vertex
        def find_DFS_path_to_setB(curr, graph:Graph):
            visited.add(curr)
            neighbors = graph.get_neighbors(curr)

            # discard neighbors which are present in separator set
            neighbors = [nbr for nbr in neighbors if nbr not in setSeparator]

            # visit neighbors in recursive manner
            for nbr in neighbors:
                if nbr in setB:
                    return True
                if nbr not in visited:
                    if find_DFS_path_to_setB(nbr, graph):
                        return True
            
            return False

        # applying BFS to check if the path exist to setB, this could be more efficient than DFS
        def find_BFS_path_to_setB(curr, graph:Graph):
            visited.add(curr)
            listNextLevelBFS = deque()
            listNextLevelBFS.append(curr)

            # keep checking till queue is not empty
            while len(listNextLevelBFS) != 0:
                vertex = listNextLevelBFS.popleft()
                neighbors = graph.get_neighbors(vertex)
                # discard neighbors which are present in separator set
                neighbors = [nbr for nbr in neighbors if nbr not in setSeparator]

                for nbr in neighbors:
                    if nbr in setB:
                        return True
                    if nbr not in visited:
                        visited.add(nbr)
                        listNextLevelBFS.append(nbr)

        # make Graph object for simplicity
        graph = Graph(moralizedMatrix)
        visited = set()

        # check from every vertex in setA if there is path to setB
        for start in setA:
            if find_DFS_path_to_setB(start, graph):
                return True

        return False

    graph = Graph(adjacency_matrix)

    # take union of setA, setB and setSeparator
    unionSetABSeparator = setA.union(setB.union(setSeparator))

    # find ancestral set
    ancestralSet = find_ancestral_set(setA=unionSetABSeparator, graph=graph)

    # create induced subgraph from acestral set
    inducedSubgraph = find_induced_subgraph(vertices=list(ancestralSet), graph=graph)

    # convert induced subgraph to moralized graph
    moralizedInducedSubgraph = get_moralize_matrix(inducedSubgraph)

    # check if the setA is connected with setB given a separator setC
    return not is_connected(setA, setB, setSeparator, moralizedInducedSubgraph)
