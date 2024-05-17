from src.simulator.Simulator_platform import *
from src.rebalancer.rebalancer_ilp_assignment import *


# rebalance vehicles to area of nearst rejected orders
def rebalancer_njo(reqs: List[Req], vehs: List[Veh], system_time: float):
    if DEBUG_PRINT: 
        print(f"    *Rebalancing idle vehicles to area of nearst rejected orders", end=" ")
    # get idle and rebalancing vehicles
    avaliable_vehs = [veh for veh in vehs if veh.status == VehicleStatus.IDLE or veh.status == VehicleStatus.REBALANCING]
    # get rejected requests
    rejected_reqs = [req for req in reqs if req.Status == OrderStatus.REJECTED]
    if len(rejected_reqs) == 0: #no rejected requests
        return
    
    # 1. Compute all possible veh-req pairs, each indicating that the request can be served by the vehicle.
    candidate_veh_req_pairs, considered_vehs = compute_candidate_veh_req_pairs(rejected_reqs, avaliable_vehs, system_time)
    # 1.1 Remove identical vehs in considered_vehs
    considered_vehs = list(set(considered_vehs))

    # 2. Compute the assignment policy, indicating which vehicle to pick which request.
    selected_veh_req_pair_indices = rebalancer_ilp_assignment(candidate_veh_req_pairs, rejected_reqs, considered_vehs)

    # 3. Update the assigned vehicles' schedules and the assigned requests' statuses.
    upd_schedule_for_vehicles_in_selected_vt_pairs(candidate_veh_req_pairs, selected_veh_req_pair_indices)
        

def compute_candidate_veh_req_pairs(reqs: List[Req], vehs:List[Veh], system_time: float) \
        -> List[Tuple[Veh, List[Req], List[Tuple[int, int, int, float]], float, float]]:    
    if DEBUG_PRINT:
        print("                *Computing candidate vehicle order pairs for rebalancing...", end=" ")

    # Each veh_req_pair = [veh, trip, sche, cost, score]
    candidate_veh_req_pairs = []
    considered_vehs = []

    # 1. Compute all veh-req pairs for new received requests.
    for req in reqs:
        available_veh = []
        for veh in vehs: 
            # Check if the vehicle can reach the origin node before the MAX_DELAY_REBALANCE
            time_to_origin = get_timeCost(veh.current_node, req.Ori_id)
            if time_to_origin > MAX_DELAY_REBALANCE:
                continue
            available_veh.append([veh, time_to_origin])

        if len(available_veh) == 0: #no vehicle can reach the origin node before the MAX_DELAY_REBALANCE
            continue

        if HEURISTIC_ENABLE: # enable heuristic method to accelerate
            # if too many vehicles, we can use a heuristic to reduce the number of vehicles to consider
            if len(available_veh) > MAX_NUM_VEHICLES_TO_CONSIDER:
                available_veh.sort(key = lambda x: x[1])
                available_veh = available_veh[:MAX_NUM_VEHICLES_TO_CONSIDER]

            # Delete time to origin and add vehicle to considered_vehs
            available_veh = [available_veh[0] for available_veh in available_veh]
            considered_vehs.extend(available_veh)   

        else: # disable heuristic method, modify data structure
            available_veh = [available_veh[0] for available_veh in available_veh]

        # All other vehicles are able to serve current request, find best schedule for each vehicle.
        for veh in available_veh:
            best_sche, cost = compute_schedule(veh, req)
            candidate_veh_req_pairs.append([veh, req, best_sche, cost, 0.0]) #vt_pair = [veh, trip, sche, cost, score]

    return candidate_veh_req_pairs, considered_vehs

def compute_schedule(veh: Veh, req: Req):
    # best_schedule = None
    # min_time_cost = np.inf
    # veh.schedule = veh.remove_duplicate_sublists(veh.schedule)

    # current_schedule = copy.deepcopy(veh.schedule) 
    # current_schedule = pickle.loads(pickle.dumps(veh.schedule))

    # assert current_schedule != None #DEBUG CODE, current_schedule should be None
    # assert len(current_schedule) < 5 #DEBUG CODE

    # [Rebalance_target_node, rebalance_node_type, Fake_num_people, fake_latest_pu_time, rebalancer_req_ID]
    current_schedule = [[req.Ori_id, 0, req.Num_people, req.Latest_PU_Time, req.Shortest_TT, 0]] # 0 means rebalance schedule
    time_cost = get_timeCost(veh.current_node, req.Ori_id)

    return current_schedule, time_cost


def compute_schedule_time_cost(schedule: list): 
    total_schedule_time = 0.0
    for i in range(len(schedule) - 1):
        total_schedule_time += get_timeCost(schedule[i][0], schedule[i+1][0])

    return total_schedule_time


def insert_request_into_schedule(schedule: list, request: Req, PU_node_position: int, DO_node_position: int):
    PU_node = [request.Ori_id, 1, request.Num_people, request.Latest_PU_Time, request.Shortest_TT]
    DO_node = [request.Des_id, -1, request.Num_people, request.Latest_DO_Time, request.Shortest_TT]
    # new_schedule = copy.deepcopy(schedule)
    new_schedule = pickle.loads(pickle.dumps(schedule))
    new_schedule.insert(PU_node_position, PU_node)
    new_schedule.insert(DO_node_position, DO_node)
    return new_schedule


def upd_schedule_for_vehicles_in_selected_vt_pairs(candidate_veh_trip_pairs: list,
                                                   selected_veh_trip_pair_indices: List[int]):
    # assigned_reqs = []
    for idx in selected_veh_trip_pair_indices:
        #For Simonetto's Method, there is only one req for each trip.
        [veh, req, sche, cost, score] = candidate_veh_trip_pairs[idx]
        veh.update_schedule(sche)
        veh.status = VehicleStatus.REBALANCING
        req.Status = OrderStatus.REJECTED_REBALANCED
        # assigned_reqs.append(req)
    # return assigned_reqs
        