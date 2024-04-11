"""
definition of vehicles for the AMoD system
"""

from route_functions import *
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

    def move_to_time(self, current_system_time:float): 
        while self.veh_time < current_system_time and len(self.route) > 0: #update veh_time until it reaches current_system_time

            arc_time = retrive_TimeCost(self.current_node, self.target_node)
            self.time_to_complete_current_arc = arc_time * (1 - self.arc_completion_percentage)

            if self.veh_time + self.time_to_complete_current_arc <= current_system_time: #able to complete the arc
                self.veh_time += self.time_to_complete_current_arc
                self.arc_completion_percentage = 0
                self.current_node = self.target_node
                self.route.pop(0)
                if len(self.route) == 0: #no more nodes to visit
                    self.status = VehicleStatus.IDLE  
                    self.veh_time = current_system_time #vehicle will stay idle until next round of requests
                else: #update target node
                    self.target_node = self.route[0]

            else: #unable to complete the arc
                self.arc_completion_percentage = (current_system_time - self.veh_time)/arc_time + self.arc_completion_percentage
                self.veh_time = current_system_time

    
