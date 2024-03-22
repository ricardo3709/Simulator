"""
single request batch assignment, where requests cannot be combined in the same interval
"""

from src.dispatcher.ilp_assign import *


def assign_orders_through_sba(current_cycle_requests: list[Req], vehs: list[Veh], system_time: float):
    if DEBUG_PRINT:
        print(f"        -Assigning {len(current_cycle_requests)} orders to vehicles through SBA...")

    # 1. Compute all possible veh-req pairs, each indicating that the request can be served by the vehicle.
    candidate_veh_req_pairs = compute_candidate_veh_req_pairs(current_cycle_requests, vehs, system_time)

    # 2. Score the candidate veh-req pairs.
    score_vt_pairs_with_num_of_orders_and_sche_cost(candidate_veh_req_pairs, current_cycle_requests, system_time)
    # score_vt_pairs_with_num_of_orders_and_value_of_post_decision_state(len(new_received_rids), vehs,
    #                                                                    candidate_veh_req_pairs, value_func,
    #                                                                    system_time_sec)

    # 3. Compute the assignment policy, indicating which vehicle to pick which request.
    selected_veh_req_pair_indices = ilp_assignment(candidate_veh_req_pairs, new_received_rids, reqs, vehs)
    # selected_veh_req_pair_indices = greedy_assignment(feasible_veh_req_pairs)

    # 000. Convert and store the vehicles' states at current epoch and their post-decision states as an experience.
    # if COLLECT_DATA and verify_the_current_epoch_is_in_the_main_study_horizon(system_time_sec):
    #     value_func.store_vehs_state_to_replay_buffer(len(new_received_rids), vehs,
    #                                                  candidate_veh_req_pairs, selected_veh_req_pair_indices,
    #                                                  system_time_sec)

    # 4. Update the assigned vehicles' schedules and the assigned requests' statuses.
    upd_schedule_for_vehicles_in_selected_vt_pairs(candidate_veh_req_pairs, selected_veh_req_pair_indices)

    if DEBUG_PRINT:
        num_of_assigned_reqs = 0
        for rid in new_received_rids:
            if reqs[rid].status == OrderStatus.PICKING:
                num_of_assigned_reqs += 1
        print(f"            +Assigned orders: {num_of_assigned_reqs} ({timer_end(t)})")


def compute_candidate_veh_req_pairs(current_cycle_requests: list[Req], vehs:list[Veh], system_time: float) \
        -> List[Tuple[Veh, List[Req], List[Tuple[int, int, int, float]], float, float]]:    
    if DEBUG_PRINT:
        print("                *Computing candidate vehicle order pairs...", end=" ")

    # Each veh_req_pair = [veh, trip, sche, cost, score]
    candidate_veh_req_pairs = []

    # 1. Compute the feasible veh-req pairs for new received requests.
    for req in current_cycle_requests:
        req_params = [req.Req_ID, req.Ori_id, req.Des_id, req.Latest_PU_Time, req.Latest_DO_Time]
        for veh in vehs:
            if get_duration_from_origin_to_dest(veh.nid, req.Ori_id) + veh.t_to_nid + system_time > req.Latest_PU_Time:
                continue
            veh_params = [veh.nid, veh.t_to_nid, veh.load]
            sub_sche = veh.sche
            best_sche, cost, feasible_sches = compute_schedule(veh_params, [sub_sche], req_params, system_time)
            if best_sche:
                candidate_veh_req_pairs.append([veh, [req], best_sche, cost, 0.0])

    # 2. Add the basic schedule of each vehicle, which denotes the "empty assign" option in ILP.
    for veh in vehs:
        candidate_veh_req_pairs.append([veh, [], copy.copy(veh.sche), compute_sche_cost(veh, veh.sche), 0.0])

    return candidate_veh_req_pairs
