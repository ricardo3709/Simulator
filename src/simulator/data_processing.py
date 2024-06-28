import numpy as np
import pickle
import pandas as pd
from src.simulator.config import *

def feature_preparation(state):
    node_lookup_table = pd.read_csv(PATH_MANHATTAN_NODES_LOOKUP_TABLE)
    area_ids = node_lookup_table['zone_id'].unique().astype(int)

    [avaliable_veh_nodes, working_veh_nodes, gen_counts_areas, rej_counts_areas, attraction_counts_areas] = state

    # request_gen_counts = [sum(gen_counts_areas[i]) for i in range(1,len(gen_counts_areas)+1)]
    request_gen_counts = [sum(d)for d in gen_counts_areas.values()]
    request_rej_counts = [sum(d)for d in rej_counts_areas.values()]
    request_attraction_counts = [sum(d)for d in attraction_counts_areas.values()]

    avaliable_veh_areas = np.zeros((63,2))
    avaliable_veh_areas[:,0] = area_ids
    working_veh_areas = np.zeros((63,2))
    working_veh_areas[:,0] = area_ids
    
    for idx, counts in enumerate(avaliable_veh_nodes):
        node_id = idx + 1 
        area_id = node_lookup_table[node_lookup_table['node_id'] == node_id]['zone_id'].values[0]
        indice = np.where(avaliable_veh_areas[:,0] == area_id)[0]
        avaliable_veh_areas[indice,1] += counts
        
    
    for idx, counts in enumerate(working_veh_nodes):
        node_id = idx + 1 
        area_id = node_lookup_table[node_lookup_table['node_id'] == node_id]['zone_id'].values[0]
        indice = np.where(working_veh_areas[:,0] == area_id)[0]
        working_veh_areas[indice,1] += counts

    avaliable_veh_areas_col = avaliable_veh_areas[:,1]
    working_veh_areas_col = working_veh_areas[:,1]
    request_gen_counts_areas_col = request_gen_counts
    request_rej_counts_areas_col = request_rej_counts
    request_attraction_counts_areas_col = request_attraction_counts
    # area_ids = torch.tensor(avaliable_veh_areas[:, 0]).to(device)
    features_tensor = np.stack(
        [avaliable_veh_areas_col,
        working_veh_areas_col,
        request_gen_counts_areas_col,
        request_rej_counts_areas_col,
        request_attraction_counts_areas_col],
        axis=0
    ).transpose(1, 0).astype(np.float32) # [63, 5]

    return features_tensor