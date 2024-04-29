"""
route planning functions
"""
import copy
import pickle
import os.path as osp
from src.simulator.config import *

# BASEDIR = osp.dirname(osp.abspath(__file__))

if MAP_NAME == "SmallGrid":
    PATH_ALL_PATH_TABLE = PATH_SMALLGRID_ALL_PATH_TABLE
    number_of_nodes = NUM_NODES_SMALLGRID
elif MAP_NAME == "Manhattan":
    PATH_ALL_PATH_TABLE = PATH_MANHATTAN_ALL_PATH_MATRIX
    number_of_nodes = NUM_NODES_MANHATTAN 


with open(PATH_ALL_PATH_TABLE, 'rb') as f:
    ALL_PATH_TABLE = pickle.load(f)

print(f"[INFO] Route functions are ready. ")

def check_problem_node(number_of_nodes: int):
    wrong_nodes_pair = []
    for i in range (0,number_of_nodes):
        for j in range (0,number_of_nodes):
            route = retrieve_route(i,j)
            if route == []:
                wrong_nodes_pair.append([i,j])
    return wrong_nodes_pair

def retrieve_route(origin: int, destination: int):
        if MAP_NAME == "SmallGrid":
            route = copy.deepcopy(ALL_PATH_TABLE[origin][destination][0])
        elif MAP_NAME == "Manhattan":
            pass
        else:
            raise ValueError("Invalid MAP_NAME")
        return route
    
def retrive_TimeCost(origin: int, destination: int):
        if MAP_NAME == "SmallGrid":
            time = copy.deepcopy(ALL_PATH_TABLE[origin][destination][1]) * 1.5 
        elif MAP_NAME == "Manhattan":
            pass
        else:
            raise ValueError("Invalid MAP_NAME")
        return time

def get_route_by_matrix(Oid: int, Did: int, all_path_matrix):
    current_node = Oid
    route = [Oid]

    while current_node != Did:
        next_node = all_path_matrix[current_node][Did]
        route.append(next_node)         
        current_node = next_node
        
    route.append(Did)
    return route
    