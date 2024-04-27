"""
compute an assignment plan from all possible matches
"""

from src.dispatcher.scheduling import *
import gurobipy as gp
from gurobipy import GRB
from typing import List, Tuple


def ilp_assignment(veh_trip_pairs: List[Tuple[Veh, List[Req], List[Tuple[int, int, int, float]], float, float]], #list[[Veh, list[Req], list[(int, int, int, float)], float, float]]
                #    considered_rids: List[int],
                   reqs: List[Req],
                   vehs: List[Veh],
                   ensure_assigning_orders_that_are_picking: bool = True) -> List[int]:
    
    # Create a new model
    model = gp.Model("ilp")
    model.setParam("LogToConsole", 0) #0: no log output, 1: log output

    PENALTY = 40.0 #penalty for ignoring a vehicle-trip pair
    vehicle_check = [] #check if vehicle is assigned, 1 for assigned, 0 for not assigned
    request_check = [] #check if request is assigned, 1 for assigned, 0 for not assigned
    veh_trip_pairs_check = [] #check if vehicle-trip pair is assigned, 1 for assigned, 0 for not assigned
    selected_veh_trip_pair_indices = []

    # Declare Model Variables
    for i in range(len(vehs)):
        vehicle_check.append(model.addVar(vtype=GRB.BINARY)) # (lb = 0.0, ub = 1.0, obj = 0.0, vtype = GRB.BINARY)
    for i in range(len(reqs)):
        request_check.append(model.addVar(vtype=GRB.BINARY))
    for i in range(len(veh_trip_pairs)):
        veh_trip_pairs_check.append(model.addVar(vtype=GRB.BINARY))
    
    # Constrain 1: each vehicle can only be assigned at most one veh_trip_pair(request).
    for i in range(len(vehs)): #iterates over vehicles
        for j in range(len(veh_trip_pairs)): #iterates over vehicle-trip pairs
            if veh_trip_pairs[j][1] == None: #empty assign
                continue
            if vehs[i] == veh_trip_pairs[j][0]: #veh_trip_pairs contain current vehicle
                vehicle_check[i] += veh_trip_pairs_check[j] 
        model.addConstr(vehicle_check[i] <= 1.0) #Number of constrain equal to number of vehicles
    
    # Constrain 2: each request can only be assigned to at most one veh_trip_pair(vehicle).
    for i in range(len(reqs)): #iterates over requests
        for j in range(len(veh_trip_pairs)): #iterates over vehicle-trip pairs
            if veh_trip_pairs[j][1] == None: #empty assign
                continue
            if reqs[i] in veh_trip_pairs[j]: #veh_trip_pairs contain current request
                request_check[i] += veh_trip_pairs_check[j]
        model.addConstr(request_check[i] <= 1.0) #Number of constrain equal to number of requests
    
    # Objective: minimize the total delay of all veh_trip_pairs.
    object_score = 0.0

    for i in range(len(veh_trip_pairs)): #veh_trip_pairs = [veh, trip, sche, cost, score], len(veh_trip_pairs) = len(veh_trip_pairs_check)
        if veh_trip_pairs[i][1] == None: #empty assign
            continue
        time_to_origin = retrive_TimeCost(veh_trip_pairs[i][0].current_node, veh_trip_pairs[i][1].Ori_id) #time to travel to origin node, also need to be minimized
        # object_score = Delay + Time_to_Origin(Pickup) + Penalty_of_Ignoring, for each veh_trip_pair
        object_score += veh_trip_pairs_check[i] * (veh_trip_pairs[i][4] + time_to_origin) + (1.0 - veh_trip_pairs_check[i]) * PENALTY
    
    model.setObjective(object_score, GRB.MINIMIZE) #set the objective function to be minimized
    
    # Optimize model.
    model.optimize()

    # Get the result.
    for veh_trip_pair_idx, veh_trip_pairs_status in enumerate(veh_trip_pairs_check): 
        if veh_trip_pairs_status.getAttr(GRB.Attr.X) == 1:
            selected_veh_trip_pair_indices.append(veh_trip_pair_idx) #index of selected vehicle-trip pairs, optimized by ILP

    return selected_veh_trip_pair_indices #index of selected vehicle-trip pairs, optimized by ILP

    
    
    considered_rids = [req.Req_ID for req in reqs]
    if DEBUG_PRINT:
        print(f"                *ILP assignment with {len(veh_trip_pairs)} pairs...", end=" ")

    selected_veh_trip_pair_indices = []
    if len(veh_trip_pairs) == 0: #no vehicle-trip pair
        return selected_veh_trip_pair_indices
    
    # The order in which the vt-pairs are arranged can slightly affect the results. Reordering aims to eliminate it.
    veh_trip_pairs.sort(key=lambda e: e[0].id)

    try:
        # 1. Create a new model
        model = gp.Model("ilp")

        model.setParam("LogToConsole", 0) #0: no log output, 1: log output
        # model.setParam("Threads", 6)

        # 2. Create variables. vt_pair means vehicle-trip pair
        # A batch of requests is assigned to a vehicle-trip pair. We try to find the optimal assignment.
        var_vt_pair = []  # var_vt_pair[i] = 1 indicates selecting the i_th vehicle_trip_pair.
        for i in range(len(veh_trip_pairs)):
            var_vt_pair.append(model.addVar(vtype=GRB.BINARY)) # (lb = 0.0, ub = 1.0, obj = 0.0, vtype = GRB.BINARY)        
        var_order = []  # var_order[j] = 0 indicates assigning the i_th order in the list.
        for j in range(len(considered_rids)):
            var_order.append(model.addVar(vtype=GRB.BINARY)) # (lb = 0.0, ub = 1.0, obj = 0.0, vtype = GRB.BINARY)        

        # 3. Set objective: minimize Σ var_vt_pair[i] * score(vt_pair). var_vt_pair is binary, score is float.
        # Currently using delay as score, need to minimize delay.
        obj_expr = 0.0
        for i in range(len(veh_trip_pairs)):
            obj_expr += var_vt_pair[i] * veh_trip_pairs[i][4] # score
        # model.setObjective(obj_expr, GRB.MAXIMIZE) #set the objective function to be maximized
        model.setObjective(obj_expr, GRB.MINIMIZE) #set the objective function to be minimized

        # 4. Add constraints.
        #   (0) Get the pairs' indices for each vehicle and request
        vt_idx = [[] for v in range(len(vehs))]
        rt_idx = [[] for j in range(len(considered_rids))]
        for idx, [veh, trip, sche, cost, score] in enumerate(veh_trip_pairs):
            #skip all "empty assign" pairs
            if trip == None:
                continue
            vt_idx[veh.id].append(idx)
            req = trip #for Simonetto's Method, there is only one request in each trip. Save this line for future use.
                # DEBUG codes
                # if req.id not in considered_rids:
                #     print(f"[DEBUG2] req {req.Req_ID} {req.Status}, "
                #           f"request time {req.Req_Time}, latest pickup {req.Latest_PU_Time}, pickup time {req.Actual_PU_Time}")
                #     print(f"veh {veh.id}, at {veh.veh_time}s, onboard_rids {veh.onboard_rid}")
                #     print(f"sche {sche}")
                #     continue
            rt_idx[considered_rids.index(req.Req_ID)].append(idx)
        
        #   (1) Add constraint 1: each vehicle (v) can only be assigned at most one schedule (trip).
        #     Σ var_vt_pair[i] * Θ_vt(v) = 1, ∀ v ∈ V (Θ_vt(v) = 1 if v is in vt).
        #   iterates over vehicles. Each entry of vt_idx is a list of indices of vehicle-trip pairs.
        #   each vehicle may have multiple vehicle-trip pairs, but only one can be selected.
        #   thus, the sum of all selected vehicle-trip pairs for a vehicle should be less than or equal to 1.
        for indices in vt_idx: 
            con_this_veh = 0.0
            for i in indices:
                con_this_veh += var_vt_pair[i]
            model.addConstr(con_this_veh <= 1) #change to <= 1 to allow empty assign

        #   (2) Add constraint 2: each order/request (r) can only be assigned to at most one vehicle.
        #     Σ var_vt_pair[i] * Θ_vt(r) + var_order[j] = 1, ∀ r ∈ R. (Θ_vt(order) = 1 if r is in vt).
        for j, indices in enumerate(rt_idx):
            con_this_req = 0.0
            for i in indices:
                con_this_req += var_vt_pair[i]
            con_this_req += var_order[j]
            model.addConstr(con_this_req <= 1) #change to <= 1 to allow empty assign
            
        #   (3) Add constraint 3: no currently picking order is ignored.
        #     var_order[j] = 0, ∀ r ∈ R_picking
        if ensure_assigning_orders_that_are_picking:
            for j in range(len(considered_rids)):
                # if reqs[considered_rids[j]].status == OrderStatus.PICKING: #check status of all considered orders
                #     model.addConstr(var_order[j] == 0)
                if reqs[j].Status == OrderStatus.PICKING:
                    model.addConstr(var_order[j] == 0)

        # 5. Optimize model.
        model.optimize()

        # 6. Get the result.
        for i, var_vt in enumerate(var_vt_pair): #BUG: No. of vt_pairs with value 1 not equal to the number of reqs.
            if var_vt.getAttr(GRB.Attr.X) == 1:
                selected_veh_trip_pair_indices.append(i)

    except gp.GurobiError as e:
        print(f"\n[GUROBI] Error code = {str(e.message)} ({str(e)}).")
    except AttributeError:
        print("Encountered an attribute error")

    # if DEBUG_PRINT:
        # print(f"({timer_end(t)})")

    return selected_veh_trip_pair_indices #index of selected vehicle-trip pairs, optimized by ILP


def greedy_assignment(veh_trip_pairs: List[Tuple[Veh, List[Req], List[Tuple[int, int, int, float]], float, float]]) -> List[int]:
    if DEBUG_PRINT:
        print(f"                *Greedy assignment with {len(veh_trip_pairs)} pairs...", end=" ")

    selected_veh_trip_pair_indices = []
    if len(veh_trip_pairs) == 0:
        return selected_veh_trip_pair_indices
    veh_trip_pairs.sort(key=lambda e: -e[4])

    selected_vids = []
    selected_rids = []

    for idx, [veh, trip, sche, cost, score] in enumerate(veh_trip_pairs):
        # Check if the vehicle has been selected.
        if veh.id in selected_vids:
            continue
        # Check if any request in the trip has been selected.
        T_id = [r.id for r in trip]
        if np.any([rid in selected_rids for rid in T_id]):
            continue
        # The current vehicle_trip_pair is selected.
        selected_vids.append(veh.id)
        selected_rids.extend(T_id)
        selected_veh_trip_pair_indices.append(idx)

    # if DEBUG_PRINT:
        # print(f"({timer_end(t)})")

    return selected_veh_trip_pair_indices
