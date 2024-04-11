from config import * #defines the constants
import pandas as pd
import numpy as np
from vehicle import Veh
from src.simulator.request import Req
from src.simulator.statistic import Statistic
from src.simulator.route_functions import *
from src.dispatcher.dispatch_sba import *
from src.rebalancer.rebalancer_npo import *
import os.path as osp

ALLPATHTABLE = 'SmallGrid_AllPathTable.pickle'
NETWORK_NAME = 'SmallGridData'
BASEDIR = osp.dirname(osp.abspath(__file__))

with open(BASEDIR + './' + NETWORK_NAME, + '/' + ALLPATHTABLE, 'rb') as f:
    all_path_table = pickle.load(f)


class Simulator_Platform(object):
     
    def __init__(self, simulation_start_time_stamp: float):
        self.statistic = Statistic() #initialize the statistic class, Need to check whether there will be multiple instances of this class

        self.start_time = simulation_start_time_stamp
        self.system_time = self.start_time
        self.end_time = self.start_time + SIMULATION_DURATION
        self.recorded_end_time = self.start_time

        # Initialize the fleet with random initial positions.
        self.vehs = []
        for i in range(FLEET_SIZE):
            node_id = np.random.randint(1, 101)
            self.vehs.append(Veh(i, self.system_time, node_id, VEH_CAPACITY))

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
        else:
            assert (False and "[ERROR] WRONG REBALANCER SETTING! Please check the name of rebalancer in config!")
       
        print(f"[INFO] Platform is ready. ")


    def run_simulation(self) -> list:        
        for current_step_time in tqdm(range(self.start_time, self.end_time, TIME_STEP), desc=f"Ricardo's Simulator"):
            self.end_time_stamp = current_step_time
            self.system_time = current_step_time
            self.run_cycle(current_step_time)
    

    def run_cycle(self, current_step_time: float):
        # 1. Update the vehicles' positions and the orders' statuses.
        self.update_veh_req_to_current_time()

        # 2. Pick up requests in the current cycle.
        current_cycle_requests = self.get_current_cycle_request(current_step_time)

        # 3. Assign pending orders to vehicles.
        availiable_vehicels = self.get_availiable_vehicels()

        if self.dispatcher == DispatcherMethod.SBA:
            assign_orders_through_sba(current_cycle_requests, availiable_vehicels, current_step_time)
      
        # 4. Reposition idle vehicles to high demand areas.
        if self.rebalancer == RebalancerMethod.NPO:
            reposition_idle_vehicles_to_nearest_pending_orders(self.reqs, self.vehs)
    
    
    # update vehs and reqs status to their planned positions at time self.system_time
    def update_veh_req_to_current_time(self):
        if DEBUG_PRINT:
            print(f"        -Updating vehicles positions and orders statuses to time {self.system_time}...")

        # update the vehicles' positions to the current time
        for veh in self.vehs:
            Veh.move_to_time(veh, self.system_time)

        # Reject the long waited orders.
        for req in self.reqs:
            if req.Status != OrderStatus.PENDING:
                continue
            if self.system_time >= req.Request_time + req.Max_wait or self.system_time >= req.Latest_PU_Time:
                req.Status = OrderStatus.REJECTED
                self.statistic.total_rejected_requests += 1

    def get_current_cycle_request(self, current_time) -> list:
        current_cycle_requests = []
        for req in self.reqs:
            if current_time - TIME_STEP < req.Req_time <= current_time:
                current_cycle_requests.append(req)
                
        return current_cycle_requests

    def get_availiable_vehicels(self) -> list: #vehicle should has at least 1 capacity
        availiable_vehicels = []
        for veh in self.vehs:
           if veh.load < veh.capacity:
               availiable_vehicels.append(veh)
        
        return availiable_vehicels
    
    def create_report(self):
        print(f"Simulation Report:")
        print(f"Total Requests: {self.statistic.total_requests}")
        print(f"Total Rejected Requests: {self.statistic.total_rejected_requests}")