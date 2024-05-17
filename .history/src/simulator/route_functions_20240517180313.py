"""
route planning functions
"""
import copy
import pickle
import os.path as osp
import pandas as pd
from src.simulator.config import ConfigManager

# BASEDIR = osp.dirname(osp.abspath(__file__))
class RouteFunctions:
    def __init__(self):
        self.config = ConfigManager()

        if self.config.get('MAP_NAME') == "SmallGrid":
            PATH_ALL_PATH_TABLE = self.config.get('PATH_SMALLGRID_ALL_PATH_TABLE')
            number_of_nodes = self.config.get('NUM_NODES_SMALLGRID')
        elif self.config.get('MAP_NAME') == "Manhattan":
            PATH_ALL_PATH_TABLE = self.config.get('PATH_MANHATTAN_ALL_PATH_MATRIX')
            number_of_nodes = self.config.get('NUM_NODES_MANHATTAN') 


        with open(PATH_ALL_PATH_TABLE, 'rb') as p:
            self.ALL_PATH_TABLE = pickle.load(p)

        with open(self.config.get('PATH_MANHATTAN_ALL_PATH_TIME_MATRIX'), 'rb') as t:
            self.ALL_PATH_TIME_MATRIX = pickle.load(t)

        with open(self.config.get('PATH_MANHATTAN_CITYARC'), 'rb') as cityarc:
            self.CITYARC = pickle.load(cityarc)

        # print(f"[INFO] Route functions are ready. ")

    def check_problem_node(number_of_nodes: int):
        wrong_nodes_pair = []
        for i in range (0,number_of_nodes):
            for j in range (0,number_of_nodes):
                route = self.get_route(i,j)
                if route == []:
                    wrong_nodes_pair.append([i,j])
        return wrong_nodes_pair

    def get_route(self, origin: int, destination: int):
            # if self.config.get('MAP_NAME') == "SmallGrid":
            #     route = pickle.loads(pickle.dumps(ALL_PATH_TABLE[origin][destination][0])) #deepcopy. accerlate with pickle
            #     # route = copy.deepcopy(ALL_PATH_TABLE[origin][destination][0])
            # elif self.config.get('MAP_NAME') == "Manhattan":
            #     route = get_route_by_matrix(origin, destination, ALL_PATH_TABLE) #No need to deepcopy
            #     # route = copy.deepcopy(get_route_by_matrix(origin, destination, ALL_PATH_TABLE))
            # else:
            #     raise ValueError("Invalid self.config.get('MAP_NAME')")
            # return route
            route = self.get_route_by_matrix(origin, destination, self.ALL_PATH_TABLE) #No need to deepcopy
            return route
        
    def get_timeCost(self, origin: int, destination: int):
            # if self.config.get('MAP_NAME') == "SmallGrid":
            #     time = pickle.loads(pickle.dumps(ALL_PATH_TABLE[origin][destination][1]))*1.5 #deepcopy. accerlate with pickle
            #     # time = copy.deepcopy(ALL_PATH_TABLE[origin][destination][1]) * 1.5 
            # elif self.config.get('MAP_NAME') == "Manhattan":
            #     time = ALL_PATH_TIME_MATRIX[origin][destination] #deepcopy. accerlate with pickle
            #     # time = copy.deepcopy(ALL_PATH_TIME_MATRIX[origin][destination])
            # else:
            #     raise ValueError("Invalid self.config.get('MAP_NAME')")
            # return time
            time = self.ALL_PATH_TIME_MATRIX[origin][destination] #deepcopy. accerlate with pickle
            return time


    def get_route_by_matrix(self, Oid: int, Did: int, all_path_matrix):
        current_node = Oid
        route = [Oid]
        # time_cost = 0.0

        while current_node != Did:
            next_node = pickle.loads(pickle.dumps(int(all_path_matrix[current_node][Did]))) #deepcopy. accerlate with pickle
            # next_node = copy.deepcopy(int(all_path_matrix[current_node][Did]))

            # time_to_next_node = all_path_time_matrix[current_node][next_node]
            route.append(next_node)         
            # time_cost += time_to_next_node
            current_node = next_node

        return route

    def get_surrounding_nodes(self, target_node, num_layers):
        connected_nodes = set()
        connected_nodes.add(target_node)
        
        for layer in range(1, num_layers+1):
            new_nodes = set()
            for node in connected_nodes:
                new_nodes.update(self.CITYARC[node][self.CITYARC[node] == 1].index)
            connected_nodes.update(new_nodes)
        
        return connected_nodes