from config import * #defines the constants
import pandas as pd
import numpy as np
from src.simulator.vehicle import Veh
from src.simulator.request import Req
from src.simulator.route_functions import *

class Simulator_Platform(object):
     
    def __init__(self, simulation_start_time_stamp: float):
        
        self.start_time = simulation_start_time_stamp
        self.system_time = self.start_time
        self.end_time = self.start_time + SIMULATION_DURATION
        self.recorded_end_time = self.start_time


        # Initialize the fleet.
        self.vehs = []
        # num_of_stations = get_num_of_vehicle_stations()
        # for i in range(FLEET_SIZE[0]):
        #     station_idx = int(i * num_of_stations / FLEET_SIZE[0])
        #     nid = get_vehicle_station_id(station_idx)
        #     [lng, lat] = get_node_geo(nid)
        #     self.vehs.append(Veh(i, nid, lng, lat, VEH_CAPACITY[0], self.system_time_sec))
        for i in range(FLEET_SIZE[0]): #randomly assign vehicles to nodes
            nid = np.random.randint(1, 101)
            [lng, lat] = get_node_geo(nid) # WIP: get_node_geo is not implemented
            self.vehs.append(Veh(i, nid, lng, lat, VEH_CAPACITY[0], self.start_time))
       

        # Initialize the demand generator.
        self.reqs = []
        reqs = pd.read_csv(PATH_SMALLGRID_REQUESTS)
        self.reqs_data = reqs.to_numpy()
        self.req_init_idx = 0
        print(f"[INFO] Demand Generator is ready. ")

        # Initialize the dispatcher and the rebalancer.
        if DISPATCHER == "SBA":
            self.dispatcher = DispatcherMethod.SBA
        # elif DISPATCHER == "OSP-NR":
        #     self.dispatcher = DispatcherMethod.OSP_NR
        # elif DISPATCHER == "OSP":
        #     self.dispatcher = DispatcherMethod.OSP
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
        # Frames record the states of the AMoD model for animation purpose
        frames_system_states = []

        if DEBUG_PRINT:
            # for epoch_start_time_sec in range(0, self.system_shutdown_time_sec, CYCLE_S[0]):
            #     self.run_cycle(epoch_start_time_sec)
            #     if RENDER_VIDEO and self.main_sim_start_time_sec <= epoch_start_time_sec < self.main_sim_end_time_sec:
            #         frames_system_states.append(copy.deepcopy(self.vehs))
            pass
        else:
            for current_step_time in tqdm(range(self.start_time, self.end_time, TIME_STEP), desc=f'AMoD'): #AMOD is prefix
                self.end_time_stamp = current_step_time
                self.system_time = current_step_time
                self.run_cycle(current_step_time)
                
                # if RENDER_VIDEO and self.main_sim_start_time_sec <= epoch_start_time_sec < self.main_sim_end_time_sec:
                #     frames_system_states.append(copy.deepcopy(self.vehs))

        return frames_system_states
    
    def run_cycle(self, current_step_time: float):
        # 1. Update the vehicles' positions and the orders' statuses.
        self.upd_vehs_and_reqs_stat_to_time()

        # 2. Generate new reqs.
        new_received_rids = self.gen_reqs_to_time()

        # 3. Assign pending orders to vehicles.
        for veh in self.vehs:
            veh.sche_has_been_updated_at_current_epoch = False
        if verify_the_current_epoch_is_in_the_main_study_horizon(epoch_end_time_sec):
            if self.dispatcher == DispatcherMethod.SBA:
                assign_orders_through_sba(new_received_rids, self.reqs, self.vehs, self.system_time_sec,
                                          self.value_func)
            elif self.dispatcher == DispatcherMethod.OSP_NR:
                assign_orders_through_osp(new_received_rids, self.reqs, self.vehs, self.system_time_sec,
                                          self.value_func, is_reoptimization=False)
            elif self.dispatcher == DispatcherMethod.OSP:
                assign_orders_through_osp(new_received_rids, self.reqs, self.vehs, self.system_time_sec,
                                          self.value_func)
        else:
            assign_orders_through_sba(new_received_rids, self.reqs, self.vehs, self.system_time_sec, self.value_func)

        # 4. Reposition idle vehicles to high demand areas.
        if self.rebalancer == RebalancerMethod.NPO:
            reposition_idle_vehicles_to_nearest_pending_orders(self.reqs, self.vehs, self.system_time_sec,
                                                               len(new_received_rids), self.value_func)
            
    def upd_vehs_and_reqs_stat_to_time(self):
        if DEBUG_PRINT:
            print(f"        -Updating vehicles positions and orders statuses to time {self.system_time}...")

        # Advance the vehicles by the whole cycle.
        for veh in self.vehs:
            done = veh.move_to_time(self.system_time, False)
            for (rid, pod, time_of_arrival) in done:
                if pod == 1:
                    self.reqs[rid].update_pick_info(time_of_arrival)
                elif pod == -1:
                    self.reqs[rid].update_drop_info(time_of_arrival)

        # Reject the long waited orders.
        for req in self.reqs:
            if req.status != OrderStatus.PENDING:
                continue
            if self.system_time_sec >= req.Tr + 150 or self.system_time_sec >= req.Clp:
                req.status = OrderStatus.WALKAWAY

        
