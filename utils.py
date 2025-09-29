####################################
# Author: Jeremy (Meng-Chieh) Lee  #
# Email	: mengchil@cs.cmu.edu      #
####################################

import pickle
from graphviz import Digraph
from graph import *

def draw_graph(g, path, label):
    G = Digraph()
    G.attr(label=label, fontsize='20')
    nodes = {}
    edges = collections.defaultdict(int)
    for e in g.edges.values():
        s, d = str(e.frm), str(e.to)
        nodes[s] = str(g.vertices[e.frm].vlb)
        nodes[d] = str(g.vertices[e.to].vlb)
        edges[(s, d)] = e.weight
    for idx, n in enumerate(nodes.keys()):
        G.node(n, n + ' (' + nodes[n] + ')')
    for e in edges.keys():
        G.edge(e[0], e[1], str(edges[e]))
    G.render(path, format='png', cleanup=True)

def read_graphs(file_name):
    with open(file_name, 'rb') as handle:
        data = pickle.load(handle)

    graphs = dict()
    for idx, g in enumerate(data):
        # Handle different pickle file structures
        if isinstance(g, tuple):
            # Some pickle files contain tuples with (graph, value)
            networkx_graph = g[0]
        else:
            # Other pickle files contain the graph directly
            networkx_graph = g
            
        tgraph = Graph(idx, eid_auto_increment=True)
        # Convert networkx 3.x view objects to lists for compatibility
        for n in list(networkx_graph.nodes()):
            tgraph.add_vertex(int(n), str(networkx_graph.nodes[n]['type']))
        for e in list(networkx_graph.edges()):
            tgraph.add_edge(AUTO_EDGE_ID, int(e[0]), int(e[1]), 1, int(networkx_graph.edges[e]['weight']))
        graphs[idx] = tgraph

    return graphs
