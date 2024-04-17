from src.simulator.config import * #defines the constants
import pandas as pd
import numpy as np
from src.simulator.vehicle import Veh
from src.simulator.request import Req
from src.simulator.statistic import Statistic
# from src.simulator.route_functions import *
from src.dispatcher.dispatch_sba import *
from src.rebalancer.rebalancer_npo import *
from src.rebalancer.rebalancer_njo import *
from tqdm import tqdm
import os.path as osp

ALLPATHTABLE = 'SmallGrid_AllPathTable.pickle'
NETWORK_NAME = 'SmallGridData'
BASEDIR = osp.dirname(osp.abspath(__file__))

with open(osp.join(BASEDIR, '../..', NETWORK_NAME, ALLPATHTABLE), 'rb') as f:
# with open(BASEDIR + '/' + NETWORK_NAME+ '/' + ALLPATHTABLE, 'rb') as f:
    all_path_table = pickle.load(f)


class Simulator_Platform(object):
     
    def __init__(self, simulation_start_time_stamp: float):
        self.statistic = Statistic() #initialize the statistic class, Need to check whether there will be multiple instances of this class
        self.start_time = simulation_start_time_stamp
        self.system_time = self.start_time
        self.end_time = self.start_time + SIMULATION_DURATION
        self.recorded_end_time = self.start_time
        self.total_time_step = SIMULATION_DURATION // TIME_STEP
        self.accumulated_request = []

        # Initialize the fleet with random initial positions.
        self.vehs = []
        for i in range(FLEET_SIZE[0]):
            node_id = np.random.randint(0, 100)
            self.vehs.append(Veh(i, self.system_time, node_id, VEH_CAPACITY[0]))

        # Initialize the demand generator.
        self.reqs = []
        reqs = pd.read_csv(PATH_SMALLGRID_REQUESTS)
        reqs_data = reqs.to_numpy()
        for i in range(reqs_data.shape[0]):
            self.reqs.append(Req(int(reqs_data[i, 0]), int(reqs_data[i, 1]), float(reqs_data[i, 2]), int(reqs_data[i, 3]), float(reqs_data[i, 4]), int(reqs_data[i, 5])))
        
        self.req_init_idx = 1
        self.statistic.total_requests = len(self.reqs)
        print(f"[INFO] Demand Generator is ready. ")

        # Initialize the dispatcher and the rebalancer.
        if DISPATCHER == "SBA":
            self.dispatcher = DispatcherMethod.SBA
        else:
            assert (False and "[ERROR] WRONG DISPATCHER SETTING! Please check the name of dispatcher in config!")
        if REBALANCER == "NONE":
            self.rebalancer = RebalancerMethod.NONE
        elif REBALANCER == "NPO":
            self.rebalancer = RebalancerMethod.NPO
        elif REBALANCER == "NJO":
            self.rebalancer = RebalancerMethod.NJO
        else:
            assert (False and "[ERROR] WRONG REBALANCER SETTING! Please check the name of rebalancer in config!")
       
        print(f"[INFO] Platform is ready. ")


    def run_simulation(self):        
        for current_time_step in tqdm(range(max(int(self.start_time),1), int(self.total_time_step)+1, 1), desc=f"Ricardo's Simulator"):
            current_actual_time = current_time_step * TIME_STEP
            self.end_time_stamp = current_actual_time
            self.system_time = current_actual_time
            self.run_cycle()
        
    

    def run_cycle(self):
        # 1. Update the vehicles' positions
        self.update_veh_to_time()

        # 2. Pick up requests in the current cycle. add the requests to the accumulated_request list
        current_cycle_requests = self.get_current_cycle_request(self.system_time)

        # 2.1 Prune the accumulated requests. (Assigned requests and rejected requests are removed.)
        self.accumulated_request.extend(current_cycle_requests)
        self.prune_requests()
        # print(f"        -Considered current cycle requests: {len(self.accumulated_request)}")
        # self.reject_long_waited_requests()

        # 3. Assign pending orders to vehicles.
        availiable_vehicels = self.get_availiable_vehicels()
        if self.dispatcher == DispatcherMethod.SBA:
            assign_orders_through_sba(self.accumulated_request, availiable_vehicels, self.system_time)
      
        # 4. Reposition idle vehicles to high demand areas.
        if self.rebalancer == RebalancerMethod.NPO:
            reposition_idle_vehicles_to_nearest_pending_orders(self.accumulated_request, self.vehs)
        elif self.rebalancer == RebalancerMethod.NJO:
            rebalancer_njo(self.reqs, self.vehs, self.system_time)


    def prune_requests(self):
        if DEBUG_PRINT:
            print("                *Pruning candidate vehicle order pairs...", end=" ")

        req_to_be_pruned = []
        for req in self.accumulated_request:
            # 1. Remove the assigned requests from the accumulated requests.
            if req.Status == OrderStatus.PICKING:
                req_to_be_pruned.append(req)
            # 2. Remove the rejected requests from the accumulated requests.
            elif req.Status == OrderStatus.REJECTED:
                req_to_be_pruned.append(req)
        self.accumulated_request = [req for req in self.accumulated_request if req not in req_to_be_pruned]
    
    def reject_long_waited_requests(self):
        # Reject the long waited orders.
        for req in self.accumulated_request:
            if req.Status != OrderStatus.PENDING:
                continue
            if self.system_time >= req.Req_time + req.Max_wait or self.system_time >= req.Latest_PU_Time:
                req.Status = OrderStatus.REJECTED
                # self.statistic.total_rejected_requests += 1
                # print(f"Request {req.Req_ID} has been rejected.")
                # print(f"Total Rejected Requests: {self.statistic.total_rejected_requests}")
    
    # update vehs and reqs status to their planned positions at time self.system_time
    def update_veh_to_time(self):
        if DEBUG_PRINT:
            print(f"        -Updating vehicles positions and orders statuses to time {self.system_time}...")

        # update the vehicles' positions to the current time
        for veh in self.vehs:
            veh.move_to_time(self.system_time, self.statistic)


    def get_current_cycle_request(self, current_time) -> list:
        current_cycle_requests = []
        for req in self.reqs:
            #EXP: to make it faster. Assume the requests are sorted by Req_time    
            if req.Req_time > current_time:
                break

            elif current_time - TIME_STEP < req.Req_time:
                current_cycle_requests.append(req)
            
                
        return current_cycle_requests

    def get_availiable_vehicels(self) -> list: #vehicle should has at least 1 capacity
        availiable_vehicels = []
        for veh in self.vehs:
           if veh.load < veh.capacity:
               availiable_vehicels.append(veh)
        
        return availiable_vehicels
    
    def create_report(self):
        for req in self.reqs:
            if req.Status == OrderStatus.REJECTED or req.Status == OrderStatus.REJECTED_REBALANCED:
                self.statistic.total_rejected_requests += 1
            elif req.Status == OrderStatus.PICKING:
                self.statistic.total_served_requests += 1

        avg_req_shortest_TT = np.mean([req.Shortest_TT for req in self.reqs])
        # avg_veh_runtime = self.statistic.total_veh_run_time / len(self.vehs)
        print(f"Simulation Report:")
        print(f"Total Requests: {len(self.reqs)}")
        print(f"Total Rejected Requests: {self.statistic.total_rejected_requests}")
        print(f"Total Served Requests: {self.statistic.total_served_requests}")
        print(f"Average Shortest Travel Time: {avg_req_shortest_TT}")
        # print(f"Average Vehicle Runtime: {avg_veh_runtime}")