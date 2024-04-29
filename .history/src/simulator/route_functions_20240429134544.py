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

with open(PATH_MANHATTAN_ALL_PATH_TIME_MATRIX, 'rb') as f:
    ALL_PATH_TIME_MATRIX = pickle.load(f)

print(f"[INFO] Route functions are ready. ")

def check_problem_node(number_of_nodes: int):
    wrong_nodes_pair = []
    for i in range (0,number_of_nodes):
        for j in range (0,number_of_nodes):
            route = get_route(i,j)
            if route == []:
                wrong_nodes_pair.append([i,j])
    return wrong_nodes_pair

def get_route(origin: int, destination: int):
        if MAP_NAME == "SmallGrid":
            route = copy.deepcopy(ALL_PATH_TABLE[origin][destination][0])
        elif MAP_NAME == "Manhattan":
            route, _ = copy.deepcopy(get_route_and_time_by_matrix(origin, destination, ALL_PATH_TABLE, ALL_PATH_TIME_MATRIX))
        else:
            raise ValueError("Invalid MAP_NAME")
        return route
    
def get_timeCost(origin: int, destination: int):
        if MAP_NAME == "SmallGrid":
            time = copy.deepcopy(ALL_PATH_TABLE[origin][destination][1]) * 1.5 
        elif MAP_NAME == "Manhattan":
            _ , time = copy.deepcopy(get_route_and_time_by_matrix(origin, destination, ALL_PATH_TABLE, ALL_PATH_TIME_MATRIX))
        else:
            raise ValueError("Invalid MAP_NAME")
        return time

def get_route_and_time_by_matrix(Oid: int, Did: int, all_path_matrix, all_path_time_matrix):
    current_node = Oid
    route = [Oid]
    time_cost = 0.0

    while current_node != Did:
        next_node = int(all_path_matrix[current_node][Did])
        time_to_next_node = all_path_time_matrix[current_node][Did]
        route.append(next_node)         
        time_cost += time_to_next_node
        current_node = next_node

    route.append(Did)

    return route, time_cost
