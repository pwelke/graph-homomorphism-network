import networkx as nx
import random
import itertools
import matplotlib.pyplot as plt

from ghc.utils.DISCio import DISChom

import numpy as np


def random_ktree_decomposition(N, k, seed=None):
    '''Sample a random ktree on N vertices.
    
    To this end, draw a random tree that defines the topology of the 
    tree decomposition and then randomly create bags for a full, nice 
    tree decomposition.
    '''

    if k > N - 1:
        raise ValueError(f'k(={k})+1 cannot be larger than N(={N})')

    # if N == 1:
    #     T = nx.Graph()
    #     T.add_node(1)
    #     return [], (T, [[1]])

    # if k < N:
    # sample a random tree for the tree decomposition
    T = nx.generators.random_tree(N-k, seed=seed)
    bfs = nx.bfs_edges(T, 0)

    # else:
    #     # the tree is a singleton
    #     T = nx.Graph()
    #     T.add_node(1)

    rnd = random.seed(seed)

    # construct bags of a k-tree. The first bag consists of the first k+1 vertices and is fully connected
    bags = [None for _ in range(N-k)]
    bags[0] = [v for v in range(k+1)] # I assume shuffling is not necessary, as T is random
    edges = [e for e in itertools.combinations(bags[0], 2)]

    candidates = [v for v in range(k+1, N)]

    for i, e in enumerate(bfs):
        bag = bags[e[0]].copy()
        deleted_vertex = bag.pop(random.randint(0, k-1))
        new_vertex = candidates[i]
        for v in bag:
            edges.append((v, new_vertex))
        bag.append(new_vertex)
        bags[e[1]] = bag
        
    tree_decomposition = (T, bags)

    return edges, tree_decomposition


def erdos_filter(edges, p=0.9, seed=None):
    '''Delete edges from edge list i.i.d. with probability 1-p.
    I.e., keep any edge with probability p'''

    random.seed(seed)

    filtered_edges = list()
    for e in edges:
        if random.random() < p:
            filtered_edges.append(e)

    return filtered_edges


def connected_filter(P):
    '''Return the list of connected components, as networkx graphs'''

    S = [P.subgraph(c).copy() for c in nx.connected_components(P)]
    return S


def partial_ktree_sample(N, k, p, seed=None):
    '''Returns a list of networkx graphs that are the connected components of a 
    partial ktree that was obtained by deleting edges with probability p from a 
    random k tree on N vertices. '''

    edges, td = random_ktree_decomposition(N, k, seed=seed)
    filtered_edges = erdos_filter(edges, p=p, seed=seed)
    filtered_graph = nx.empty_graph(n=N)
    filtered_graph.add_edges_from(filtered_edges)
    connected_components = connected_filter(filtered_graph)

    return connected_components



def Nk_strategy(max_size, pattern_count, p=0.35):

    # draw sizes from uniform distribution
    sizes = np.random.randint(2, max_size+1, size=pattern_count)

    # draw treewidths from geometric distribution, but bounded by size - 1
    treewidths = np.random.default_rng().geometric(p=p, size=pattern_count)
    treewidths = np.where(treewidths<sizes-1, treewidths, sizes - 1)

    return sizes, treewidths


def random_ktree_profile(graphs, size=6, density=False, seed=8, pattern_count=50, **kwargs):

    tw_downweighting_p = 0.35
    partial_ktree_edge_keeping_p = 0.9

    
    kt_list = list()
    while len(kt_list) < pattern_count:
        
        sizes, treewidths = Nk_strategy(max_size=size, pattern_count=1, p=tw_downweighting_p)

        kt_list += filter(lambda p: len(p.nodes) > 1, partial_ktree_sample(N=sizes[0], k=treewidths[0], p=partial_ktree_edge_keeping_p))
        
    kt_list = kt_list[:pattern_count] # the above might result in more than pattern_count patterns

    # homX = list()
    # for G in graphs:
    #     homX += [hom(G, kt, density=density) for kt in kt_list]
    # return homX

    return DISChom(pattern_list=kt_list, graph_list=graphs)


if __name__ == '__main__':

    pattern_list = [nx.path_graph(i) for i in range(2,5)]
    graph_list = [nx.path_graph(i) for i in range(2,10)]
    
    random_ktree_profile(graph_list)

    # connected_patterns = partial_ktree_sample(7, 1, 0.9)

    # for P in connected_patterns:
    #     nx.draw_kamada_kawai(P)
    #     plt.show()


    # # print(Nk_strategy(6, 10))
