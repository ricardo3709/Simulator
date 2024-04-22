"""
route planning functions
"""
import copy
import pickle
import os.path as osp
from src.simulator import const

# with open(PATH_SMALLGRID_ARCS, "rb") as f:
#     network_arcs = pd.read_csv(f)
# with open(PATH_SMALLGRID_TIMECOST, "rb") as f:
#     network_timecost = pd.read_csv(f)
# with open(PATH_SMALLGRID_REQUESTS, "rb") as f:
#     network_requests = pd.read_csv(f)    

ALLPATHTABLE = 'SmallGrid_AllPathTable.pickle'
NETWORK_NAME = 'SmallGridData'
BASEDIR = osp.dirname(osp.abspath(__file__))
number_of_nodes = 100

with open(osp.join(BASEDIR, '../..', NETWORK_NAME, ALLPATHTABLE), 'rb') as f:
# with open(BASEDIR + '/' + NETWORK_NAME+ '/' + ALLPATHTABLE, 'rb') as f:
    ALL_PATH_TABLE = copy.deepcopy(pickle.load(f))

# wrong_nodes_pair = check_problem_node(number_of_nodes)
const.backup_all_path_table = copy.deepcopy(ALL_PATH_TABLE)
# assert len(wrong_nodes_pair) == 0 #check if there is any problem with the path table

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
        route = backup_all_path_table[origin][destination][0]
        # if origin == destination:
        #     route = [origin]
        return route
    
def retrive_TimeCost(origin: int, destination: int):
        time = backup_all_path_table[origin][destination][1]
        return time



# replace by retrieve_time_cost
# get the duration of the best route from origin to destination
# def get_duration_from_origin_to_dest(onid: int, dnid: int) -> float:
#     duration = network_timecost[onid - 1][dnid - 1] #onid/dnid - 1 because the index starts from 0
#     assert duration != -1
#     return duration


# get the distance of the best route from origin to destination
# def get_distance_from_origin_to_dest(onid: int, dnid: int) -> float:
#     # distance = travel_distance_table[onid - 1][dnid - 1]
#     distance = get_duration_from_origin_to_dest(onid, dnid) * TAXI_SPEED_meter_per_min
#     assert distance != -1
#     return distance


# replace by retrieve_route
# get the best route from origin to destination
# def build_route_from_origin_to_dest(onid: int, dnid: int) -> Tuple[float, float, List[Tuple]]:
#     # 1. recover the best path from origin to destination from the path table
#     path = [dnid]
#     pre_node = shortest_path_table[onid - 1][dnid - 1]
#     while pre_node > 0:
#         path.append(pre_node)
#         pre_node = shortest_path_table[onid - 1][pre_node - 1]
#     path.reverse()

#     # 2. get the route information from origin to destination
#     duration = 0.0
#     distance = 0.0
#     steps = []
#     for i in range(len(path) - 1):
#         u = path[i]
#         v = path[i + 1]
#         t = network_timecost[u - 1][v - 1]
#         d = get_duration_from_origin_to_dest(u-1,v-1)
#         u_geo = get_node_geo(u)
#         v_geo = get_node_geo(v)
#         steps.append((t, d, [u, v], [u_geo, v_geo]))
#         duration += t
#         distance += d
#     tnid = path[-1]
#     tnid_geo = get_node_geo(tnid)
#     steps.append((0.0, 0.0, [tnid, tnid], [tnid_geo, tnid_geo]))

#     # check the accuracy of routing.
#     deviation_due_to_data_structure = 0.005
#     assert (abs(duration - network_timecost[onid - 1][dnid - 1])
#             <= deviation_due_to_data_structure)
#     assert (abs(distance - get_duration_from_origin_to_dest(onid - 1, dnid - 1))
#             <= deviation_due_to_data_structure)

#     return duration, distance, steps


# return the geo of node [lng, lat]
# Not Needed for now
# def get_node_geo(nid: int) -> List[float]:
#     pos = network_nodes[nid - 1]
#     return [pos.lng, pos.lat]


# def get_num_of_vehicle_stations() -> int:
#     return len(vehicle_stations)


# def get_vehicle_station_id(station_index: int) -> int:
#     return vehicle_stations[station_index].node_id
