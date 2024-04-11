"""
single request batch assignment, where requests cannot be combined in the same interval
"""

from src.dispatcher.ilp_assign import *
from src.utility.utility_functions import *


def assign_orders_through_sba(current_cycle_requests: List[Req], vehs: List[Veh], system_time: float):
    if DEBUG_PRINT:
        print(f"        -Assigning {len(current_cycle_requests)} orders to vehicles through SBA...")

    # 1. Compute all possible veh-req pairs, each indicating that the request can be served by the vehicle.
    candidate_veh_req_pairs = compute_candidate_veh_req_pairs(current_cycle_requests, vehs, system_time)

    # WIP: Not sure if the following code is necessary, use delay for score first. 
    # 2. Score the candidate veh-req pairs. 
    score_vt_pair_with_delay(candidate_veh_req_pairs)

    # 3. Compute the assignment policy, indicating which vehicle to pick which request.
    selected_veh_req_pair_indices = ilp_assignment(candidate_veh_req_pairs, current_cycle_requests, vehs)
    # selected_veh_req_pair_indices = greedy_assignment(feasible_veh_req_pairs)

    # 000. Convert and store the vehicles' states at current epoch and their post-decision states as an experience.
    # if COLLECT_DATA and verify_the_current_epoch_is_in_the_main_study_horizon(system_time_sec):
    #     value_func.store_vehs_state_to_replay_buffer(len(new_received_rids), vehs,
    #                                                  candidate_veh_req_pairs, selected_veh_req_pair_indices,
    #                                                  system_time_sec)

    # 4. Update the assigned vehicles' schedules and the assigned requests' statuses.
    upd_schedule_for_vehicles_in_selected_vt_pairs(candidate_veh_req_pairs, selected_veh_req_pair_indices)

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
        for veh in vehs: 
            time_to_origin = retrive_TimeCost(veh.current_node, req.Ori_id)
            if time_to_origin + system_time > req.Latest_PU_Time: #vehicle cannot reach the origin node before the latest pickup time
                continue
            # All other vehicles are able to serve current request, find best schedule for each vehicle.
            best_sche, cost, feasible_sches = compute_schedule(veh, req, system_time)
            if best_sche: #best schedule exists
                candidate_veh_req_pairs.append([veh, req, best_sche, cost, 0.0]) #vt_pair = [veh, trip, sche, cost, score]

    # 2. Add the basic schedule of each vehicle, which denotes the "empty assign" option in ILP.
    for veh in vehs:
        candidate_veh_req_pairs.append([veh, None, copy.copy(veh.schedule), compute_schedule_time_cost(veh.schedule), 0.0])

    return candidate_veh_req_pairs
