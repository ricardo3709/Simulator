"""
prepare network data for the simulation
convert csv to pickle
"""

import time
import pickle
import math
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm

def load_network():
    """
    Load the network data from the csv files
    """
    # Load the network data from the csv files
    print('Loading network data...')
    df_Arcs = pd.read_csv('SmallGrid_Arcs.csv')
    df_TimeCost = pd.read_csv('SmallGrid_TimeCost.csv')

    G = nx.DiGraph()
    num_edges = df_Arcs.sum() #num of edges is num of non-zero elements in the Arcs matrix
    rng = tqdm(df_Arcs.iterrows(), total=num_edges, ncols=100, desc='Building network') #ncols is the width of the progress bar
    for idx, arc in rng:
        idx = idx
        arc = arc

