"""
compute all feasible schedules for a given vehicle v and a trip T.
"""
import copy

from src.simulator.request import Req
from src.simulator.vehicle import Veh
from src.simulator.route_functions import *
from src.utility.utility_functions import *
from typing import List, Tuple, Union

def score_vt_pair_with_delay(candidate_veh_trip_pairs: list):
    #candidate_veh_trip_pairs[veh, req, sche, cost, score]
    for vt_pair_idx in range(len(candidate_veh_trip_pairs)): 
        delay = compute_schedule_delay(candidate_veh_trip_pairs[vt_pair_idx][2], candidate_veh_trip_pairs[vt_pair_idx][0])
        candidate_veh_trip_pairs[vt_pair_idx][4] = delay

def compute_schedule_delay(schedule:list, veh:Veh): #sum(time of nodes to nodes) - sum(shortest time for all trips)
    #schedule = [node[node_id, type, num_people, max_wait_time, shortest_Trip_Time(only for PU node)]], type = 1 for PU, -1 for DO
    total_delay = 0.0
    shortest_time = 0.0
    actual_time = veh.time_to_complete_current_arc
    
    actual_time += compute_schedule_time_cost(schedule) #sum(time of nodes to nodes)
    shortest_time = sum([node[4] for node in schedule if node[1] == 1]) #sum(shortest time for all trips)
    total_delay = actual_time - shortest_time
    return total_delay

def compute_schedule_time_cost(schedule: list): 
    total_schedule_time = 0.0
    for i in range(len(schedule) - 1):
        total_schedule_time += retrive_TimeCost(schedule[i][0], schedule[i+1][0])

    return total_schedule_time

def test_constraints(schedule: list, veh: Veh): 
    # node[node_id, type, num_people, max_wait_time, shortest_Trip_Time]
    current_load = veh.load #initial load
    max_capacity = veh.capacity #initial capacity
    current_time = veh.veh_time #initial time
    current_node = veh.current_node #initial node
    for node in schedule:
        #1. Capacity
        if node[1] == 1: #PU
            current_load += node[2] #add the number of people to the current load
            if current_load > max_capacity: #if the current load exceeds the vehicle's capacity
                return False
        elif node[1] == -1: #DO
            current_load -= node[2] #subtract the number of people from the capacity
            if current_load < 0: #if the capacity is negative
                assert "Error: Negative capacity"
                return False
        #2.1 Max Waiting for Pickup
        time_to_next_node = retrive_TimeCost(current_node, node[0]) #time to travel to node
        if node[1] == 1: #PU
            time_to_pickup = time_to_next_node #time to travel to node
            max_waiting_time_pickup = node[3] #max wait time
            if time_to_pickup > max_waiting_time_pickup:
                return False
        #2.2 Max Waiting for Dropoff
        if node[1] == -1: #DO
            accumulated_time = current_time + time_to_next_node #time to travel to node + current time
            max_detour_time_dropoff = current_time + node[4] + MAX_DETOUR_TIME 
            if accumulated_time > max_detour_time_dropoff: #if the time to travel to node exceeds the max detour
                return False
            current_time = accumulated_time #update current time
            current_node = node[0] #update current node

        # #2. Time        
        # time_to_next_node = retrive_TimeCost(current_node, node[0]) #time to travel to node
        # accumulated_time = current_time + time_to_next_node #time to travel to node + current time
        # if accumulated_time > node[3]: #if the time to travel to node exceeds the max wait time
        #     return False
        # current_time = accumulated_time #update current time
        # current_node = node[0] #update current node

    return True



def insert_request_into_schedule(schedule: list, request: Req, PU_node_position: int, DO_node_position: int):
    PU_node = [request.Ori_id, 1, request.Num_people, request.Latest_PU_Time, request.Shortest_TT]
    DO_node = [request.Des_id, -1, request.Num_people, request.Latest_DO_Time, request.Shortest_TT]
    new_schedule = copy.deepcopy(schedule)
    new_schedule.insert(PU_node_position, PU_node)
    new_schedule.insert(DO_node_position, DO_node)
    return new_schedule


def compute_schedule(veh: Veh, req: Req, system_time: float):
    feasible_schedules = []
    best_schedule = None
    min_time_cost = np.inf
    # veh.schedule = veh.remove_duplicate_sublists(veh.schedule)
    current_schedule = copy.deepcopy(veh.schedule) ####where the fuck is this element been updated?????
    # assert len(current_schedule) < 5 #DEBUG CODE

    for PU_node_position in range(len(current_schedule) + 1):
        for DO_node_position in range(PU_node_position + 1, len(current_schedule) + 2):
            new_schedule = insert_request_into_schedule(current_schedule, req, PU_node_position, DO_node_position)

            if test_constraints(new_schedule, veh): #check if the new schedule satisfies all constraints
                time_cost = compute_schedule_time_cost(new_schedule)
                feasible_schedules.append(new_schedule) #store the feasible schedule, but not the best one
                if time_cost < min_time_cost: #update the best schedule
                    best_schedule = copy.deepcopy(new_schedule)
                    min_time_cost = time_cost

    return best_schedule, min_time_cost, feasible_schedules

def upd_schedule_for_vehicles_in_selected_vt_pairs(candidate_veh_trip_pairs: list,
                                                   selected_veh_trip_pair_indices: List[int]):
    
    for idx in selected_veh_trip_pair_indices:
        
        #For Simonetto's Method, there is only one req for each trip.
        [veh, req, sche, cost, score] = candidate_veh_trip_pairs[idx]
        req.Status = OrderStatus.PICKING
        # [veh, trip, sche, cost, score] = candidate_veh_trip_pairs[idx]
        # for req in trip:
        #     req.status = OrderStatus.PICKING
        # assert len(sche) < 5 #DEBUG CODE
        veh.update_schedule(sche)
        # veh.sche_has_been_updated_at_current_epoch = True

    # if DEBUG_PRINT:
    #     print(f"                *Executing assignment with {len(selected_veh_trip_pair_indices)} pairs... "
    #           f"({timer_end(t)})")


# def score_vt_pairs_with_num_of_orders_and_sche_cost(veh_trip_pairs: list, reqs: list[Req], system_time: float):
#     # 1. Get the coefficients for NumOfOrders and ScheduleCost.
#     max_sche_cost = 1
#     for vt_pair in veh_trip_pairs: #vt_pair = [veh, trip, sche, cost, score], all eligible pairs for this cycle
#         [veh, trip, sche, cost, score] = vt_pair
#         vt_pair[3] = compute_sche_delay(veh, sche, reqs, system_time)
#         if vt_pair[3] > max_sche_cost:
#             max_sche_cost = vt_pair[3]
#     max_sche_cost = int(max_sche_cost)
#     num_length = 0
#     while max_sche_cost:
#         max_sche_cost //= 10
#         num_length += 1
#     reward_for_serving_a_req = pow(10, num_length)

#     # # 2. Score the vt_pairs with NumOfOrders and ScheduleCost.
#     # # (The objective is to maximize the number of assigned orders and minimize the schedule cost (travel delay).)
#     # for vt_pair in veh_trip_pairs:
#     #     vt_pair[4] = reward_for_serving_a_req * len(vt_pair[1]) - vt_pair[3]

#     for vt_pair in veh_trip_pairs:
#         vt_pair[4] = len(vt_pair[1])


# ("is_reoptimization" only influences the calculation of rewards in "compute_post_decision_state".)
# def score_vt_pairs_with_num_of_orders_and_value_of_post_decision_state(num_of_new_reqs: int,
#                                                                        vehs: list[Veh],
#                                                                        reqs: list[Req],
#                                                                        veh_trip_pairs: list,
#                                                                        value_func: ValueFunction,
#                                                                        system_time_sec: int,
#                                                                        is_reoptimization: bool = False):
#     expected_vt_scores = value_func.compute_expected_values_for_veh_trip_pairs(num_of_new_reqs, vehs,
#                                                                                copy.deepcopy(veh_trip_pairs),
#                                                                                system_time_sec, is_reoptimization)
#     for idx, vt_pair in enumerate(veh_trip_pairs):
#         vt_pair[4] = expected_vt_scores[idx]

    # # 1. Get the coefficients for NumOfOrders and ScheduleCost.
    # max_sche_cost = 1
    # for vt_pair in veh_trip_pairs:
    #     [veh, trip, sche, cost, score] = vt_pair
    #     vt_pair[3] = compute_sche_delay(veh, sche, reqs, system_time_sec)
    #     if vt_pair[3] > max_sche_cost:
    #         max_sche_cost = vt_pair[3]
    # max_sche_cost = int(max_sche_cost)
    # num_length = 0
    # while max_sche_cost:
    #     max_sche_cost //= 10
    #     num_length += 1
    # reward_for_serving_a_req = pow(10, num_length)
    #
    # if ONLINE_TRAINING:
    #     # 2. Score the vt_pairs with NumOfOrders and ScheduleCost.
    #     for idx, vt_pair in enumerate(veh_trip_pairs):
    #         vt_pair[4] = reward_for_serving_a_req * expected_vt_scores[idx] - vt_pair[3]
    # else:
    #     # 2. Score the vt_pairs with NumOfOrders and ScheduleCost.
    #     for idx, vt_pair in enumerate(veh_trip_pairs):
    #         vt_pair[4] = expected_vt_scores[idx]

