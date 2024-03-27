"""
prepare network data for the simulation
convert csv to pickle
"""

import pickle
import math
import numpy as np
import pandas as pd
import networkx as nx
import os.path as osp
from tqdm import tqdm

BASEDIR = osp.dirname(osp.abspath(__file__))
ARC_NAME = 'SmallGrid_Arcs.csv'
TIMECOST_NAME = 'SmallGrid_TimeCost.csv'
PICKEL_NAME = 'SmallGrid_Network.pickle'

def load_network():
    """
    Load the network data from the csv files
    """
    # Load the network data from the csv files
    print('Loading network data...')
    df_Arcs = pd.read_csv(BASEDIR + '/' + ARC_NAME)
    df_TimeCost = pd.read_csv(BASEDIR + '/' + TIMECOST_NAME)

    G = nx.DiGraph()
    num_edges = df_Arcs.sum().sum() #num of edges is num of non-zero elements in the Arcs matrix
    rng = tqdm(df_Arcs.iterrows(), total=num_edges, ncols=100, desc='Building network...') #ncols is the width of the progress bar
    for idx, arc in rng:
        connected_nodes = np.where(arc > 0)[0]
        G.add_node(idx) #add current node to the graph

        for i in connected_nodes:
            G.add_edge(idx, i, TimeCost=df_TimeCost.iloc[idx, i]) #add connected arcs to the graph
            G.add_node(i) #add the connected nodes to the graph

    print('Network data loaded.')
    print(f'Network has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.')

    # save network as pickel file
    print('Saving the network as a pickle file...')
    with open(BASEDIR + '/' + PICKEL_NAME, 'wb') as f:
        pickle.dump(G, f)



if __name__ == '__main__':
    load_network()