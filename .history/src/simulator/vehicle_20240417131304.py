"""
definition of vehicles for the AMoD system
"""

from src.simulator.route_functions import *
from src.simulator.statistic import Statistic
import numpy as np




class Veh(object):
    """
    Veh is a class for vehicles
    Attributes:
        id: vehicle ID
        status: idle/working/rebalancing
        veh_time: time recording by veh 
        arc_completion_percentage: percentage of the current arc that has been completed
        time_to_complete_current_arc: time needed to complete the current arc
        current_node: id of current node in network (last node visited by the vehicle)
        target_node: id of next node the vehicle will visit (route[0])
        route: a list of nodes that the vehicle will visit
        capacity: capacity of the vehicle
        load: number of passengers on board
        schedule: a list of nodes that the vehicle plan to visit(planned PU/DO nodes, includes visited nodes)
        
    """

    def __init__(self, id: int, system_time: float, current_node: int, capacity: int): 
        self.id = id
        self.status = VehicleStatus.IDLE
        self.veh_time = system_time
        self.arc_completion_percentage = 0.0 #update when call move_to_time
        self.time_to_complete_current_arc = 0.0 #update when call move_to_time
        self.current_node = current_node 
        self.target_node = None
        self.route = []
        self.capacity = capacity
        self.load = 0
        self.schedule = []

    # to avoid confusing, use schedule instead of route, also delete nodes in schedule after visiting it. 
    def move_to_time(self, current_system_time:float): 
        while self.veh_time < current_system_time and len(self.schedule) > 0: #update veh_time until it reaches current_system_time
            
            assert self.current_node != None

            current_target_node = self.schedule[0][0]

            #DEBUG CODE
            if type(self.current_node) == List: 
                current_node = self.current_node[0][0]
            else:
                current_node = self.current_node 

            arc_time = retrive_TimeCost(current_node, current_target_node)
            self.time_to_complete_current_arc = arc_time * (1 - self.arc_completion_percentage)

            if self.veh_time + self.time_to_complete_current_arc <= current_system_time: #able to complete the arc
                self.veh_time += self.time_to_complete_current_arc

                # for statistics
                Statistic.self.totoal_veh_run_time += self.time_to_complete_current_arc

                self.arc_completion_percentage = 0
                self.current_node = self.target_node
                self.schedule.pop(0)
                if len(self.schedule) == 0: #no more nodes to visit
                    self.status = VehicleStatus.IDLE  
                    self.veh_time = current_system_time #vehicle will stay idle until next round of requests
                else: #update target node
                    self.target_node = self.schedule[0][0]

            else: #unable to complete the arc
                self.arc_completion_percentage += (current_system_time - self.veh_time)/arc_time 
                self.veh_time = current_system_time

                # for statistics
                Statistic.self.totoal_veh_run_time += (current_system_time - self.veh_time)


    def update_schedule(self, new_schedule: list):
        # assert len(new_schedule) < 5 #DEBUG CODE
        self.schedule = new_schedule
        self.target_node = self.schedule[0][0]
        self.status = VehicleStatus.WORKING
        # self.schedule = self.remove_duplicate_sublists(self.schedule)

    def remove_duplicate_sublists(self, lst):
        seen = set()
        result = []
        for sublist in lst:
            # Convert the sublist to a tuple to make it hashable
            sublist_tuple = tuple(sublist)
            # Check if the sublist is not in the set of seen sublists
            if sublist_tuple not in seen:
                # Add the sublist to the result list
                result.append(sublist)
                # Add the sublist to the set of seen sublists
                seen.add(sublist_tuple)
        return result
