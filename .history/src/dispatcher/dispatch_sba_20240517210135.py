"""
single request batch assignment, where requests cannot be combined in the same interval
"""

from src.dispatcher.ilp_assign import *
from src.utility.utility_functions import *
from src.simulator.Simulator_platform import *

def assign_orders_through_sba(current_cycle_requests: List[Req], vehs: List[Veh], system_time: float, num_of_rejected_req_for_nodes_dict_movingAvg: dict, num_of_generate_req_for_nodes_dict_movingAvg: dict, config: ConfigManager):
    if DEBUG_PRINT:
        print(f"        -Assigning {len(current_cycle_requests)} orders to vehicles through SBA...")

    # 1. Compute all possible veh-req pairs, each indicating that the request can be served by the vehicle.
    candidate_veh_req_pairs, considered_vehs = compute_candidate_veh_req_pairs(current_cycle_requests, vehs, system_time)
    # 1.1 Remove identical vehs in considered_vehs
    considered_vehs = list(set(considered_vehs))

    # 2. Score the candidate veh-req pairs. 
    # score_vt_pair_with_delay(candidate_veh_req_pairs)

    # 3. Compute the assignment policy, indicating which vehicle to pick which request.

    #3.1 Pruning the candidate veh-req pairs. (Empty Assign)
    # candidate_veh_req_pairs = prune_candidate_veh_req_pairs(candidate_veh_req_pairs)
    
    selected_veh_req_pair_indices = ilp_assignment(candidate_veh_req_pairs, current_cycle_requests, considered_vehs, num_of_rejected_req_for_nodes_dict_movingAvg, num_of_generate_req_for_nodes_dict_movingAvg, config)
    # selected_veh_req_pair_indices = greedy_assignment(feasible_veh_req_pairs)

    # 000. Convert and store the vehicles' states at current epoch and their post-decision states as an experience.
    # if COLLECT_DATA and verify_the_current_epoch_is_in_the_main_study_horizon(system_time_sec):
    #     value_func.store_vehs_state_to_replay_buffer(len(new_received_rids), vehs,
    #                                                  candidate_veh_req_pairs, selected_veh_req_pair_indices,
    #                                                  system_time_sec)

    # 4. Update the assigned vehicles' schedules and the assigned requests' statuses.
    assigned_reqs = upd_schedule_for_vehicles_in_selected_vt_pairs(candidate_veh_req_pairs, selected_veh_req_pair_indices)
    # 5. Immediate reject all request that are not assigned.
    immediate_reject_unassigned_requests(current_cycle_requests, assigned_reqs, num_of_rejected_req_for_nodes_dict_movingAvg, config)


    # if DEBUG_PRINT:
    #     num_of_assigned_reqs = 0
    #     for rid in current_cycle_requests:
    #         if reqs[rid].status == OrderStatus.PICKING:
    #             num_of_assigned_reqs += 1
    #     print(f"            +Assigned orders: {num_of_assigned_reqs} ({timer_end(t)})")


def compute_candidate_veh_req_pairs(current_cycle_requests: List[Req], vehs:List[Veh], system_time: float) \
        -> List[Tuple[Veh, List[Req], List[Tuple[int, int, int, float]], float, float]]:    
    if DEBUG_PRINT:
        print("                *Computing candidate vehicle order pairs...", end=" ")

    # Each veh_req_pair = [veh, trip, sche, cost, score]
    candidate_veh_req_pairs = []
    considered_vehs = []

    # 1. Compute the feasible veh-req pairs for new received requests.
    for req in current_cycle_requests:
        available_veh = []
        for veh in vehs: 
            # Check if the vehicle can reach the origin node before the latest pickup time.
            time_to_origin = get_timeCost(veh.current_node, req.Ori_id)
            if time_to_origin + system_time > req.Latest_PU_Time: #vehicle cannot reach the origin node before the latest pickup time
                continue
            # Check if the vehicle has enough capacity to serve the request.
            if veh.capacity - veh.load < req.Num_people:
                continue
            # All other vehicles are able to serve current request, find best schedule for each vehicle.
            available_veh.append([veh,time_to_origin])
        
        if HEURISTIC_ENABLE: # enable heuristic method to accerlate =
            # if too many vehicles, we can use a heuristic to reduce the number of vehicles to consider
            if len(available_veh) > MAX_NUM_VEHICLES_TO_CONSIDER:
                available_veh.sort(key = lambda x: x[1])
                available_veh = available_veh[:MAX_NUM_VEHICLES_TO_CONSIDER]
            
            # Delete time to origin and add vehicle to considered_vehs
            available_veh = [available_veh[0] for available_veh in available_veh]
            considered_vehs.extend(available_veh)   
            
        else: # disable heuristic method, modify data structure
            available_veh = [available_veh[0] for available_veh in available_veh]

        for veh in available_veh:
            best_sche, cost = compute_schedule(veh, req)
            if best_sche: #best schedule exists
                candidate_veh_req_pairs.append([veh, req, best_sche, cost, 0.0]) #vt_pair = [veh, trip, sche, cost, score]
    
    considered_vehs = list(set(considered_vehs)) #remove duplicate vehs in considered_vehs
    return candidate_veh_req_pairs, considered_vehs

def prune_candidate_veh_req_pairs(candidate_veh_req_pairs):
    if DEBUG_PRINT:
        print("                *Pruning candidate vehicle order pairs...", end=" ")

    # for vt_pair in candidate_veh_req_pairs:
    #     veh, req, sche, cost, score = vt_pair
    #     # 1. Remove the assigned requests from the candidate list.
    #     if req.Status == OrderStatus.PICKING:
    #         candidate_veh_req_pairs.remove(vt_pair)
    #     # 2. Remove the rejected requests from the candidate list.
    #     elif req.Status == OrderStatus.REJECTED:
    #         candidate_veh_req_pairs.remove(vt_pair)

    pruned_vq_pair = []
    for vq_pair in candidate_veh_req_pairs:
        veh, req, sche, cost, score = vq_pair
        if req == None: #prune the empty assign option
            continue
        pruned_vq_pair.append(vq_pair)

    return pruned_vq_pair

def immediate_reject_unassigned_requests(current_cycle_requests: List[Req], assigned_reqs: List[Req], num_of_rejected_req_for_nodes_dict_movingAvg,config: ConfigManager):
    if DEBUG_PRINT:
        print("                *Immediate rejecting unassigned orders...", end=" ")
    REWARD_TYPE = config.get('REWARD_TYPE')
    
    if REWARD_TYPE == 'REJ':
        rej_reqs_per_nodes_dict = {i: 0 for i in range(1, NUM_NODES_MANHATTAN+1)} # {node_id: num_rej_req} used in reward calculation
    for req in current_cycle_requests:
        if req not in assigned_reqs:
            req.Status = OrderStatus.REJECTED
            rej_node_id = req.Ori_id
            if REWARD_TYPE == 'REJ':
                rej_reqs_per_nodes_dict[rej_node_id] += 1 #increment the number of rejected requests for the node

    if REWARD_TYPE == 'REJ':
        for node_id in range(1,NUM_NODES_MANHATTAN+1):
            if node_id in rej_reqs_per_nodes_dict.keys():
                num_of_rejected_req_for_nodes_dict_movingAvg[node_id].append(rej_reqs_per_nodes_dict[node_id])
            else:
                num_of_rejected_req_for_nodes_dict_movingAvg[node_id].append(0)



# def update_rejection_rates(rej_reqs_per_nodes_dict, num_of_rejected_req_for_nodes_dict_movingAvg):
#     for node_id in range(1,NUM_NODES_MANHATTAN+1):
#         if node_id in rej_reqs_per_nodes_dict.keys():
#             num_of_rejected_req_for_nodes_dict_movingAvg[node_id].append(rej_reqs_per_nodes_dict[node_id])
