import numpy as np
from .graph import Graph

# The algorithm starts with a directional edge(complexSpouseA-->immediateChidrenOfA), assuming complexSpouseA as one of the complex-spouse of a minimal complex.
# It keeps searching for its remaining complex-spouse using DFS ensuring that it is not violating the structure of a minimal complex
# If we find a structure, the edges complexSpouseA ----> immediateChidrenOfA and currentChildVertexn <----- complexSpouseB will remain in the pattern as they are


# complexSpouseA            : a node which is assumed as a complex spouse
# immediateChidrenOfA       : this is the immediate child of complexSpouseA from which DFS started
# visitedVertices           : set of visited nodes
# currentChildVertex        : current node in the DFS
# graph                     : Graph object, stores all the graph metadata
# listComplexSpouse         : list containing the pairs of complexSpouse

def find_complex_spouse(complexSpouseA:int, immediateChidrenOfA:int, visitedVertices:set, currentChildVertex:int, graph:Graph, listComplexSpouse : list):
        
        def violates_minimal_complex_structure(u, v):
            return (v in graph.get_parents(u) or u in graph.get_parents(v))

        def moralize_spouse(u, v):
            listComplexSpouse.append([u, v])

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
                moralize_spouse(complexSpouseA, complexSpouseB)
        #================================================================================

        # Keep moving ahead in DFS fashion, until we find all minimal complex
        # or return false(which means the complexSpouseA-->immediateChidrenOfA is not a part of any minimalComplex)
        visitedVertices.add(currentChildVertex)
        for neighbor in graph.get_neighbors(currentChildVertex):
            if(neighbor not in visitedVertices):
                find_complex_spouse(complexSpouseA=complexSpouseA, immediateChidrenOfA=immediateChidrenOfA, visitedVertices=visitedVertices, currentChildVertex=neighbor, graph=graph, listComplexSpouse = listComplexSpouse)
        visitedVertices.remove(currentChildVertex)

        return False

def get_moralize_matrix(adjacency_matrix):

    num_nodes = len(adjacency_matrix)
    graph = Graph(adjacency_matrix)
    
    # this is used to store all the pairs of complex spouse
    listComplexSpouse = []

    # we find out all the pairs of complex spouse in a DFS-like fashion
    num_nodes = graph.adjacency_matrix.shape[0]
    for i in range(num_nodes):
        for j in range(num_nodes):
            if(graph.is_directional_edge(i, j)):
                find_complex_spouse(complexSpouseA = i, immediateChidrenOfA = j, visitedVertices = {i}, currentChildVertex = j, graph = graph, listComplexSpouse = listComplexSpouse)

    # join all the complex spouse with undirected edge
    for complexSpouse in listComplexSpouse:
            adjacency_matrix[complexSpouse[0], complexSpouse[1]] = 1
            adjacency_matrix[complexSpouse[1], complexSpouse[0]] = 1

    # convert all undirected edges into directed edges
    for i in range(num_nodes):
        for j in range(num_nodes):
             if(graph.is_directional_edge(i, j)):
                  adjacency_matrix[j][i] = 1

    return adjacency_matrix