class Graph:
    def __init__(self, adjacency_matrix):
        self.adjacency_matrix = adjacency_matrix
        self.neighbors = self.find_neighbors()
        self.parents, self.children = self.find_parents_and_children()

    # Here we find all the neighbours of a vertex
    def find_neighbors(self):
        num_nodes = self.adjacency_matrix.shape[0]
        neighbors = {}

        for i in range(num_nodes):
            neighbors[i] = []

        for i in range(num_nodes):
            for j in range(i+1, num_nodes):
                if self.adjacency_matrix[i, j] == 1 and self.adjacency_matrix[j, i] == 1:
                    neighbors[i].append(j)
                    neighbors[j].append(i)

        return neighbors
    
    # Here we find all the parents of a node
    def find_parents_and_children(self):
        num_nodes = self.adjacency_matrix.shape[0]
        parents, children = {}, {}

        for i in range(num_nodes):
            parents[i] = set()
            children[i] = set()

        for i in range(num_nodes):
            for j in range(num_nodes):
                if self.adjacency_matrix[i, j] == 1 and self.adjacency_matrix[j, i] == 0:
                    parents[j].add(i)
                    children[i].add(j)

        return parents, children
    
    # get neighbors of a vertex
    def get_neighbors(self, vertex):
        return self.neighbors[vertex]
    
    # get parents of a vertex
    def get_parents(self, vertex):
        return self.parents[vertex]
    
    # get children of a vertex
    def get_children(self, vertex):
        return self.children[vertex]
    
    def is_directional_edge(self, u, v):
        return self.adjacency_matrix[u, v] == 1 and self.adjacency_matrix[v, u] == 0
