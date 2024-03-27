"""
compute the shortest path for every node pair
"""

import time
import pickle
import copy
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm
import os.path as osp

NETWORK_NAME = 'SmallGrid_Network.pickle'
BASEDIR = osp.dirname(osp.abspath(__file__))

with open(BASEDIR + '/' + NETWORK_NAME, 'rb') as f:
    G = pickle.load(f)

def compute_table():
    """
    Compute the shortest path for every node pair
    """
    print('Computing the shortest path for every node pair...')
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    print(f'Network has {num_nodes} nodes and {num_edges} edges.')

    #all_path_table[node] = {target_node: (path, timeCost)}
    #shortest path(list): all_path_table[node][target_node][0]
    #shortest time cost(float): all_path_table[node][target_node][1]
    all_path_table = {} 

    rng = tqdm(range(num_nodes), ncols=100, desc='Computing path table...')
    for node in rng:
        all_path_table[node] = dict(nx.single_source_dijkstra_path(G, node, cutoff=None, weight='TimeCost'))
        path = dict(nx.single_source_dijkstra_path(G, node, cutoff=None, weight='TimeCost'))
        timeCost = dict(nx.single_source_dijkstra_path_length(G, node, cutoff=None, weight='TimeCost'))
        path_timeCost_dict = {k: (path[k], timeCost[k]) for k in path.keys()}
        all_path_table[node] = path_timeCost_dict #store the path and time cost for each node
    
    print('Saving the path table as a pickle file...')
    nodes_id = list(all_path_table.keys())
    with open(BASEDIR + '/SmallGrid_PathTable.pickle', 'wb') as f:
        pickle.dump(all_path_table, f)

if __name__ == '__main__':
    compute_table()
    