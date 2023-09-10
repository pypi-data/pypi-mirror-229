import numpy as np
from .graph import Graph

# complexSpouseA ----> immediateChidrenOfA/currentChildVertex1--currentChildVertex2--currentChildVertex3--.......currentChildVertexn <----- complexSpouseB

# The algorithm starts with a directional edge(complexSpouseA-->immediateChidrenOfA), assuming complexSpouseA as one of the complex-spouse of a minimal complex.
# It keeps searching for its remaining complex-spouse using DFS ensuring that it is not violating the structure of a minimal complex
# If we find a structure, the edges complexSpouseA ----> immediateChidrenOfA and currentChildVertexn <----- complexSpouseB will remain in the pattern as they are
# Otherwise the edge complexSpouseA ----> immediateChidrenOfA will be converted to undirectional edge in the pattern


# complexSpouseA            : a node which is assumed as a complex spouse
# immediateChidrenOfA       : this is the immediate child of complexSpouseA from which DFS started
# visitedVertices           : set of visited nodes
# currentChildVertex        : current node in the DFS
# graph                     : Graph object, stores all the graph metadata

def determine_minimal_complex(complexSpouseA:int, immediateChidrenOfA:int, visitedVertices:set, currentChildVertex:int, directionalEdgesInPattern:np.array, graph:Graph):
        
        def violates_minimal_complex_structure(u, v):
            return (v in graph.get_parents(u) or u in graph.get_parents(v))
        
        def make_edge_part_of_minimal_complex(u, v):
            directionalEdgesInPattern[u, v] = 1

        # Check validity of induced subgraph after considering currentChildVertex in current path
        # Make sure that none of the visited vertices is a parent of currentChildVertex or vice versa (except complexSpouseA ----> immediateChidrenOfA)
        if currentChildVertex != immediateChidrenOfA:
            for v in visitedVertices:
                if violates_minimal_complex_structure(v, currentChildVertex):
                    return False
        
        #================================================================================
        # Second, we try to find the complexSpouseB whose only child is currentChildVertex and it has no children in visited set
        for complexSpouseB in graph.get_parents(currentChildVertex):
            foundSpouseB = True
            if(complexSpouseB == complexSpouseA and currentChildVertex == immediateChidrenOfA):
                  continue
            
            for v in visitedVertices:
                if violates_minimal_complex_structure(v, complexSpouseB):
                    foundSpouseB = False

            if foundSpouseB == True:
                make_edge_part_of_minimal_complex(complexSpouseA, immediateChidrenOfA)
                make_edge_part_of_minimal_complex(complexSpouseB, currentChildVertex)
                return True
        #================================================================================

        # Keep moving ahead in DFS fashion, until we find a minimal complex
        # or return false(which means the complexSpouseA-->immediateChidrenOfA is not a part of any minimalComplex)
        visitedVertices.add(currentChildVertex)
        for neighbor in graph.get_neighbors(currentChildVertex):
            if(neighbor not in visitedVertices):
                if determine_minimal_complex(complexSpouseA=complexSpouseA, immediateChidrenOfA=immediateChidrenOfA, visitedVertices=visitedVertices, currentChildVertex=neighbor, directionalEdgesInPattern = directionalEdgesInPattern, graph=graph):
                    return True
        visitedVertices.remove(currentChildVertex)

        return False

def get_pattern_matrix(adjacency_matrix):
    
    def edge_not_visited(i, j, directionalEdgesInPattern):
     return directionalEdgesInPattern[i,j] != 1

    def edge_not_visited(i, j, directionalEdgesInPattern):
        return directionalEdgesInPattern[i,j] != 1

    def convert_to_undirectional(i, j, directionalEdgesInPattern):
        return directionalEdgesInPattern[i, j] == 0
    

    num_nodes = len(adjacency_matrix)
    graph = Graph(adjacency_matrix)
    
    # this is used to store the directional edges which are part of at least 1 minimal complex
    directionalEdgesInPattern = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]
    directionalEdgesInPattern = np.array(directionalEdgesInPattern)

    # we find out all the edges which are part of 
    num_nodes = graph.adjacency_matrix.shape[0]
    for i in range(num_nodes):
        for j in range(num_nodes):
            if(graph.is_directional_edge(i, j) and edge_not_visited(i, j, directionalEdgesInPattern)):
                determine_minimal_complex(complexSpouseA = i, immediateChidrenOfA = j, visitedVertices = {i}, currentChildVertex = j, directionalEdgesInPattern = directionalEdgesInPattern, graph = graph)

    # convert input adjacency matrix into adjacency matrix for the pattern
    for i in range(num_nodes):
        for j in range(num_nodes):
            if graph.is_directional_edge(i, j) and convert_to_undirectional(i, j, directionalEdgesInPattern):
                adjacency_matrix[j, i] = 1


    return adjacency_matrix
