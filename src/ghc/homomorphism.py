from ghc.utils.hom import nx2homg, tree_list, cycle_list, path_list, hom_profile, tree_list_random
from ghc.generate_k_tree import partial_ktree_sample, Nk_strategy, product_graph_ktree_profile
import homlib as hl
import networkx as nx
import numpy as np
# from ghc.utils.DISCio import DISChom
from ghc.generate_k_tree import random_ktree_profile

def hom_tree(F, G):
    """Specialized tree homomorphism in Python (serializable).
    Add `indexed` parameter to count for each index individually.
    """
    def rec(x, p):
        hom_x = np.ones(len(G.nodes()), dtype=float)
        for y in F.neighbors(x):
            if y == p:
                continue
            hom_y = rec(y, x)
            aux = [np.sum(hom_y[list(G.neighbors(a))]) for a in G.nodes()]
            hom_x *= np.array(aux)
        return hom_x
    hom_r = rec(0, -1)
    return np.sum(hom_r)


def hom_tree_labeled(F, G, node_tags=None):
    """Tree homomorphism with node labels (tags).
    """
    if node_tags is None:
        print("Warning: Missing node tags.")
        return hom_tree(F, G)
    if type(node_tags) is list:
        node_tags = np.array(node_tags)
    def rec(x, p):
        hom_x = node_tags.T.copy()
        for y in F.neighbors(x):
            if y == p:
                continue
            hom_y = rec(y, x)
            aux = [np.sum(hom_y[:,list(G.neighbors(a))]) for a in G.nodes()]
            hom_x *= np.array(aux)
        return hom_x
    hom_r = rec(0, -1)
    return np.sum(hom_r, axis=1)


def hom_tree_explabeled(F, G, node_tags=None, exp=np.e):
    """Tree homomorphism with node labels (tags).
    """
    if node_tags is None:
        print("Warning: Missing node tags.")
        return hom_tree(F, G)
    if type(node_tags) is list:
        node_tags = np.array(node_tags)
    def rec(x, p):
        hom_x = np.power(exp, node_tags.T.copy())
        for y in F.neighbors(x):
            if y == p:
                continue
            hom_y = rec(y, x)
            aux = [np.sum(hom_y[:,list(G.neighbors(a))]) for a in G.nodes()]
            hom_x *= np.array(aux)
        return hom_x
    hom_r = rec(0, -1)
    return np.log(np.sum(hom_r, axis=1))


def hom(F, G, use_py=False, density=False):
    """Wrapper for the `hom` function in `homlib`."""
    # Default homomorphism function
    hom_func = hl.hom
    # Check if tree, then change the hom function
    if use_py:
        hom_func = hom_tree
    # Check and convert graph type
    if density:
        scaler = 1.0 / (G.number_of_nodes() ** F.number_of_nodes())
    else:
        scaler = 1.0
    if not use_py:
        F = nx2homg(F)
        G = nx2homg(G)
    return hom_func(F, G) * scaler


def atlas_profile(graphs, size=20, start=0, density=False, **kwargs):
    """Run homomorphism count for each graph in the nx atlas"""
    atlas_list = nx.atlas.graph_atlas_g()[start:start+size]
    homX = []
    for G in graphs:
        homX.append([hom(t, G, density=density) for t in atlas_list])
    return homX


def tree_profile(graphs, size=6, density=False, **kwargs):
    """Run tree homomorphism profile for a batch of graphs"""
    t_list = tree_list(size)
    homX = []
    for G in graphs:
        homX.append([hom(t, G, density=density) for t in t_list])
    return homX

def random_tree_profile(graphs, size=6, density=False, seed=8, **kwargs):
    """Run tree homomorphism profile for a batch of graphs"""
    t_list = tree_list_random(size, seed)
    homX = []
    for G in graphs:
        homX.append([hom(t, G, density=density) for t in t_list])
    return homX



def tree_rprofile(G, size=6, density=False, **kwargs):
    """Run tree right homomorphism profile for a single graph G."""
    t_list = tree_list(size)
    return [hom(G, t, density=density) for t in t_list]


def path_profile(G, size=6, density=False, **kwargs):
    """Run tree homomorphism profile for a single graph G."""
    p_list = path_list(size)
    return [hom(p, G, density=density) for p in p_list]


def cycle_profile(G, size=6, density=False, **kwargs):
    """Run tree homomorphism profile for a single graph G."""
    c_list = cycle_list(size)
    return [hom(c, G, density=density) for c in c_list]


def labeled_tree_profile(G, size=6, node_tags=None, **kwargs):
    """Run profile for labeled trees."""
    t_list = tree_list(size)
    hom_list = [hom_tree_labeled(t, G, node_tags) for t in t_list]
    return np.concatenate(hom_list)


def explabeled_tree_profile(G, size=6, node_tags=None, **kwargs):
    """Run profile for exponentially labeled trees."""
    t_list = tree_list(size)
    hom_list = [hom_tree_explabeled(t, G, node_tags) for t in t_list]
    return np.concatenate(hom_list)


def homomorphism_profile(graphs, size=6, node_tags=None, **kwargs):
    """Run profile for exponentially labeled trees."""
    t_list = hom_profile(size)

    embeddings = np.zeros([len(graphs), len(t_list)])
    for i, G in enumerate(graphs):
        for j, H in enumerate(t_list):
            hom_list = hom(H, G) 

    return embeddings




def get_hom_profile(f_str):
    if f_str == "labeled_tree":
        return labeled_tree_profile
    elif f_str == "labeled_tree_exp":
        return explabeled_tree_profile
    elif f_str == "tree":
        return tree_profile
    elif f_str == "random_tree":
        return random_tree_profile  
    elif f_str == "random_ktree":
        return random_ktree_profile
    elif f_str == "path":
        return path_profile
    elif f_str == "cycle":
        return cycle_profile
    elif f_str == "tree+cycle":
        return homomorphism_profile
    elif f_str == "atlas":
        return atlas_profile
    elif f_str == 'product_graph_ktree_profile':
        return product_graph_ktree_profile        
    else:  # Return all posible options
        return ["labeled_tree", "labeled_tree_exp",
                "tree", "random_tree", "path", "cycle", "tree+cycle", "atlas", "random_ktree", "product_graph_ktree_profile"]
