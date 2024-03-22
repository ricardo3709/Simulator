from config import * #defines the constants
import pandas as pd
import numpy as np
from src.simulator.vehicle import Veh
from src.simulator.request import Req
from src.simulator.route_functions import *

class Simulator_Platform(object):
     
     def __init__(self, simulation_start_time_stamp: 0
                #  value_func: ValueFunction
                ):
        
        self.start_time = simulation_start_time_stamp

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