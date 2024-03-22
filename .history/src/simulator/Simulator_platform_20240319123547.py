from config import * #defines the constants
import pandas as pd
import numpy as np

class Simulator_Platform(object):
     
     def __init__(self, taxi_data_file: str
                #  value_func: ValueFunction
                #  simulation_start_time_stamp: datetime
                ):
        
        self.taxi_data_file = taxi_data_file #SmallGrid_Requests

        # Initialize the fleet.
        self.vehs = []
        # num_of_stations = get_num_of_vehicle_stations()
        # for i in range(FLEET_SIZE[0]):
        #     station_idx = int(i * num_of_stations / FLEET_SIZE[0])
        #     nid = get_vehicle_station_id(station_idx)
        #     [lng, lat] = get_node_geo(nid)
        #     self.vehs.append(Veh(i, nid, lng, lat, VEH_CAPACITY[0], self.system_time_sec))
        for i in range(FLEET_SIZE[0]): #randomly assign vehicles to nodes
            WIP - Configure the Vehicle file first.
       

        # Initialize the demand generator.
        self.reqs = []
        reqs = pd.read_csv("{PARTIAL_PATH_TO_TAXI_DATA}{self.taxi_data_file}.csv")
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