import networkx as nx
import matplotlib.pyplot as plt
from .graph import Graph

def findPositions(amat, pos):
    graph = Graph(amat)
    visited = set()
    nodesWithNoParents = []
    X = 0
    Y = 0
    for i in range(len(amat)):
        hasNoParent = True
        for j in range(len(amat)):
            if amat[j][i] == 1 and amat[i][j] == 0:
                hasNoParent = False
                break
        if hasNoParent:
            nodesWithNoParents.append(i)
    
    queue = nodesWithNoParents

    while len(queue) != 0:
        Y = 0
        queueSize = len(queue)
        while queueSize != 0:
            node = queue.pop(0)
            visited.add(node)
            pos[node] = [X, Y]
            Y += 15
            children = list(graph.get_children(node))
            for child in children:
                if child not in visited:
                    queue.append(child)
            queueSize -= 1
        X += 20
    

def draw(amat, custom_labels:dict = {}):
    G_directed = nx.DiGraph()
    G_undirected = nx.Graph()

    nodes = [i for i in range(len(amat))]
    if len(custom_labels) == 0:
        for i in range(len(amat)):
            custom_labels[i] = str(i)
    
    G_directed.add_nodes_from(nodes)
    G_undirected.add_nodes_from(nodes)

    directed_edges = []
    undirected_edges = []

    for i in range(len(amat)):
        for j in range(len(amat[0])):
            if amat[i, j] == 1:
                if amat[j, i] == 1:
                    if j > i:
                        undirected_edges.append((i, j))
                else:
                    directed_edges.append((i, j))

    G_directed.add_edges_from(directed_edges)
    G_undirected.add_edges_from(undirected_edges)

    pos = nx.planar_layout(G_directed)
    findPositions(amat, pos)
    nx.draw(G_directed, pos, with_labels=True, labels=custom_labels, node_color='lightblue', node_size=130, font_size=7, font_weight='bold', arrows=True, connectionstyle="arc3,rad=0.1")
    nx.draw(G_undirected, pos, with_labels=False, node_color='lightblue', node_size=130, font_size=7, font_weight='bold', edgelist=undirected_edges, arrows=True, edge_color='orange', connectionstyle="arc3,rad=0.1")
    plt.savefig("graph.pdf", format="pdf", bbox_inches="tight")
    plt.show()
    