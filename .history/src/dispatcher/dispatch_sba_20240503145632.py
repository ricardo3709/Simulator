"""
single request batch assignment, where requests cannot be combined in the same interval
"""

from src.dispatcher.ilp_assign import *
from src.utility.utility_functions import *
from src.simulator.Simulator_platform import *


def assign_orders_through_sba(current_cycle_requests: List[Req], vehs: List[Veh], system_time: float, num_of_rejected_req_for_nodes_dict: dict):
    if DEBUG_PRINT:
        print(f"        -Assigning {len(current_cycle_requests)} orders to vehicles through SBA...")

    # 1. Compute all possible veh-req pairs, each indicating that the request can be served by the vehicle.
    candidate_veh_req_pairs = compute_candidate_veh_req_pairs(current_cycle_requests, vehs, system_time)

    # 2. Score the candidate veh-req pairs. 
    score_vt_pair_with_delay(candidate_veh_req_pairs)

    # 3. Compute the assignment policy, indicating which vehicle to pick which request.

    #3.1 Pruning the candidate veh-req pairs. (Empty Assign)
    # candidate_veh_req_pairs = prune_candidate_veh_req_pairs(candidate_veh_req_pairs)
    
    selected_veh_req_pair_indices = ilp_assignment(candidate_veh_req_pairs, current_cycle_requests, vehs, num_of_rejected_req_for_nodes_dict)
    # selected_veh_req_pair_indices = greedy_assignment(feasible_veh_req_pairs)

    # 000. Convert and store the vehicles' states at current epoch and their post-decision states as an experience.
    # if COLLECT_DATA and verify_the_current_epoch_is_in_the_main_study_horizon(system_time_sec):
    #     value_func.store_vehs_state_to_replay_buffer(len(new_received_rids), vehs,
    #                                                  candidate_veh_req_pairs, selected_veh_req_pair_indices,
    #                                                  system_time_sec)

    # 4. Update the assigned vehicles' schedules and the assigned requests' statuses.
    assigned_reqs = upd_schedule_for_vehicles_in_selected_vt_pairs(candidate_veh_req_pairs, selected_veh_req_pair_indices)
    # 5. Immediate reject all request that are not assigned.
    immediate_reject_unassigned_requests(current_cycle_requests, assigned_reqs, num_of_rejected_req_for_nodes_dict)

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

    # 1. Compute the feasible veh-req pairs for new received requests.
    for req in current_cycle_requests:
        available_veh = []
        for veh in vehs: 
            time_to_origin = get_timeCost(veh.current_node, req.Ori_id)
            if time_to_origin + system_time > req.Latest_PU_Time: #vehicle cannot reach the origin node before the latest pickup time
                continue
            # All other vehicles are able to serve current request, find best schedule for each vehicle.
            available_veh.append([veh,time_to_origin])
        
        # if too many vehicles, we can use a heuristic to reduce the number of vehicles to consider
        if len(available_veh) > MAX_NUM_VEHICLES_TO_CONSIDER:
            available_veh.sort(key = lambda x: x[1])
            available_veh = available_veh[:MAX_NUM_VEHICLES_TO_CONSIDER]

        for veh, _ in available_veh:
            best_sche, cost = compute_schedule(veh, req)
            if best_sche: #best schedule exists
                candidate_veh_req_pairs.append([veh, req, best_sche, cost, 0.0]) #vt_pair = [veh, trip, sche, cost, score]
    
    # Delete empty assign, not useful.
    # 2. Add the basic schedule of each vehicle, which denotes the "empty assign" option in ILP.
    # trip is None because it is "empty assign", else it should be req
    # for veh in vehs:
    #     # candidate_veh_req_pairs.append([veh, None, copy.copy(veh.schedule), compute_schedule_time_cost(veh.schedule), 0.0])
    #     candidate_veh_req_pairs.append([veh, None, [], 0.0, 0.0])

    return candidate_veh_req_pairs

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

def immediate_reject_unassigned_requests(current_cycle_requests: List[Req], assigned_reqs: List[Req], num_of_rejected_req_for_nodes_dict):
    if DEBUG_PRINT:
        print("                *Immediate rejecting unassigned orders...", end=" ")

    for req in current_cycle_requests:
        if req not in assigned_reqs:
            req.Status = OrderStatus.REJECTED
            rej_node_id = req.Ori_id
            num_of_rejected_req_for_nodes_dict[rej_node_id] += 1 #increment the number of rejected requests for the node
