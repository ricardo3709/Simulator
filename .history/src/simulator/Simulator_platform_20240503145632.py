from src.simulator.config import * #defines the constants
import pandas as pd
import numpy as np
import cv2
from src.simulator.types import *
from src.simulator.config import *
from src.simulator.vehicle import Veh
from src.simulator.request import Req
from src.simulator.statistic import Statistic
from src.simulator.route_functions import *
from src.dispatcher.dispatch_sba import *
from src.dispatcher.ilp_assign import *
from src.dispatcher.scheduling import *
from src.rebalancer.rebalancer_ilp_assignment import *
from src.rebalancer.rebalancer_npo import *
from src.rebalancer.rebalancer_njo import *
from src.utility.utility_functions import *
from tqdm import tqdm

# ALLPATHTABLE = 'SmallGrid_AllPathTable.pickle'
# NETWORK_NAME = 'SmallGridData'
# BASEDIR = osp.dirname(osp.abspath(__file__))

# with open(osp.join(BASEDIR, '../..', NETWORK_NAME, ALLPATHTABLE), 'rb') as f:
# # with open(BASEDIR + '/' + NETWORK_NAME+ '/' + ALLPATHTABLE, 'rb') as f:
#     all_path_table = pickle.load(f)


class Simulator_Platform(object):
     
    def __init__(self, simulation_start_time_stamp: float):
        self.statistic = Statistic() #initialize the statistic class, Need to check whether there will be multiple instances of this class
        self.start_time = simulation_start_time_stamp
        self.system_time = self.start_time
        self.end_time = self.start_time + SIMULATION_DURATION
        self.recorded_end_time = self.start_time
        self.total_time_step = SIMULATION_DURATION // TIME_STEP
        self.accumulated_request = []
        self.num_of_rejected_req_for_nodes_dict = {i: 0 for i in range(1, NUM_NODES_MANHATTAN+1)} # {node_id: num_of_rejected_req} used in reward calculation

        # Initialize the fleet with random initial positions.
        self.vehs = []
        # Initialize the demand generator.
        self.reqs = []

        if MAP_NAME == 'Manhattan': # [ReqID Oid Did ReqTime Size]
            reqs = pd.read_csv(PATH_MANHATTAN_REQUESTS)
            reqs_data = reqs.to_numpy()
            for i in range(reqs_data.shape[0]):
                self.reqs.append(Req(int(reqs_data[i, 0]), int(reqs_data[i, 1]), int(reqs_data[i, 2]), int(reqs_data[i, 3]), int(reqs_data[i,4])))
            print(f"[INFO] Requests Initialization finished")
            for i in range(FLEET_SIZE[0]):
                node_id = np.random.randint(1, NUM_NODES_MANHATTAN+1)
                self.vehs.append(Veh(i, self.system_time, node_id, VEH_CAPACITY[0]))
            print(f"[INFO] Vehicles Initialization finished")

        elif MAP_NAME == 'SmallGrid':
            reqs = pd.read_csv(PATH_SMALLGRID_REQUESTS)
            reqs_data = reqs.to_numpy()
            for i in range(reqs_data.shape[0]):
                self.reqs.append(Req(int(reqs_data[i, 0]), int(reqs_data[i, 1]), float(reqs_data[i, 2]), int(reqs_data[i, 3]), float(reqs_data[i, 4]), int(reqs_data[i, 5])))
            print(f"[INFO] Requests Initialization finished")
            for i in range(FLEET_SIZE[0]):
                node_id = np.random.randint(0, 100)
                self.vehs.append(Veh(i, self.system_time, node_id, VEH_CAPACITY[0]))
            print(f"[INFO] Vehicles Initialization finished")

        else:
            assert (False and "[ERROR] WRONG MAP NAME SETTING! Please check the name of map in config!")
        
        self.req_init_idx = 1
        self.statistic.total_requests = len(self.reqs)

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
        simulation_end_step = int(self.total_time_step)+1  
        cool_down_step = int(COOL_DOWN_DURATION // TIME_STEP)
        cool_down_flag = True
        for current_time_step in tqdm(range(max(int(self.start_time),1), simulation_end_step + cool_down_step, 1), desc=f"Ricardo's Simulator"):
            current_actual_time = current_time_step * TIME_STEP
            self.end_time_stamp = current_actual_time
            self.system_time = current_actual_time
            if cool_down_flag and current_time_step > cool_down_step:
                print("Cooling down...")
                cool_down_flag = False
            self.run_cycle()
            # self.statistic.all_veh_position_series.append(self.get_all_veh_positions())
        

    

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
            assign_orders_through_sba(self.accumulated_request, availiable_vehicels, self.system_time, self.num_of_rejected_req_for_nodes_dict)
      
        # 4. Reposition idle vehicles to high demand areas.
        if self.rebalancer == RebalancerMethod.NJO:
            rebalancer_njo(self.reqs, self.vehs, self.system_time)
        elif self.rebalancer == RebalancerMethod.NPO:
            reposition_idle_vehicles_to_nearest_pending_orders(self.accumulated_request, self.vehs)


    def prune_requests(self):
        if DEBUG_PRINT:
            print("                *Pruning candidate vehicle order pairs...", end=" ")

        req_to_be_pruned = []
        for req in self.accumulated_request:
            # 1. Remove the assigned requests from the accumulated requests.
            if req.Status == OrderStatus.PICKING:
                req_to_be_pruned.append(req)
            # 2. Remove the rejected requests from the accumulated requests.
            elif req.Status == OrderStatus.REJECTED or req.Status == OrderStatus.REJECTED_REBALANCED:
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
            veh.move_to_time(self.system_time)


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
        availiable_vehicels = [veh for veh in self.vehs if veh.load < veh.capacity]
        return availiable_vehicels
    
    def get_all_veh_positions(self):
        veh_positions = [veh.current_node for veh in self.vehs]
        # for veh in self.vehs:
        #     veh_positions.append(veh.current_node)
        return veh_positions

    def create_report(self):
        for req in self.reqs:
            if req.Status == OrderStatus.REJECTED or req.Status == OrderStatus.REJECTED_REBALANCED:
                self.statistic.total_rejected_requests += 1
            elif req.Status == OrderStatus.PICKING:
                self.statistic.total_served_requests += 1
            elif req.Status == OrderStatus.PENDING:
                self.statistic.total_pending_requests += 1
        
        for veh in self.vehs:
            self.statistic.total_veh_run_time += veh.run_time

        avg_req_shortest_TT = np.mean([req.Shortest_TT for req in self.reqs])
        avg_veh_runtime = self.statistic.total_veh_run_time / len(self.vehs)
        avg_req_runtime = self.statistic.total_veh_run_time / len(self.reqs)
        # self.create_video()
        print(f"Simulation Report:")
        print(f"Total Requests: {len(self.reqs)}")
        print(f"Total Rejected Requests: {self.statistic.total_rejected_requests}")
        print(f"Total Served Requests: {self.statistic.total_served_requests}")
        print(f"Total Pending Requests: {self.statistic.total_pending_requests}")
        print(f"Average Shortest Travel Time: {avg_req_shortest_TT}")
        print(f"Average Vehicle Runtime: {avg_veh_runtime}")
        print(f"Average Request Runtime: {avg_req_runtime}")
        # print(f"Video has been created.")
    
    def mapping_node_to_coordinate(self, node_id):
        map_width = 10 #adjust as needed
        video_width = 1000 #adjust as needed
        scale_factor = video_width / map_width
        return (int(node_id % 10 * scale_factor), int(node_id // 10 * scale_factor))
    
    def interpolate_position(self, vehicle_coordinates, scale_factor):
        interpolated_coordinates = []
        for frame in vehicle_coordinates:
            interpolated_coordinates.append(frame)
            next_frame = vehicle_coordinates[vehicle_coordinates.index(frame) + 1]
            for i in range(1, scale_factor):
                interpolated_frame = []
                for j in range(len(frame)):
                    interpolated_frame.append((int(frame[j][0] + (next_frame[j][0] - frame[j][0]) * i / scale_factor), int(frame[j][1] + (next_frame[j][1] - frame[j][1]) * i / scale_factor)))
                interpolated_coordinates.append(interpolated_frame)
        return interpolated_coordinates



    def create_video(self):
        # Define the size of the map and vehicles
        VIDEO_RESOLUTION = (1000,1000)  # Adjust as needed, pixels
        VEHICLE_SIZE = 10  # Adjust as needed, pixels
        VEHICLE_COLOR = (0,0,200) #Light Red color for vehicles, (Blue, Green, Red) for opencv
        GRID_SIZE = (10, 10)
        GRID_COLOR = (128,128,128)  # Grey color for grid lines
        
        # vehicle_positions = copy.deepcopy(self.statistic.all_veh_position_series)
        vehicle_positions = pickle.loads(pickle.dumps(self.statistic.all_veh_position_series))

        vehicle_coordinates = [] # List of frames, each frame is a list of vehicle coordinates
        for frame in vehicle_positions:
            frame_coordinate = []
            for veh_node_id in frame:
                veh_coordinate = self.mapping_node_to_coordinate(veh_node_id) 
                frame_coordinate.append(veh_coordinate)
            vehicle_coordinates.append(frame_coordinate)
        interpolated_vehicle_coordinates = self.interpolate_position(vehicle_coordinates, 5)

        # Create a VideoWriter object
        # cv2.cv.CV_FOURCC(*'XVID')
        # fourcc = cv2.VideoWriter_fourcc(*'XVID')
        
        FILE_TYPE = '.mp4'
        # BASEDIR = osp.dirname(osp.abspath(__file__)) + '/'
        OUTPUT_NAME = str(FLEET_SIZE[0]) + 'Vehs_' + str(VEH_CAPACITY[0]) + 'Ppl_' + str(MAX_PICKUP_WAIT_TIME) + 'MaxWait_' + str(MAX_DETOUR_TIME) + 'MaxDetour_' + REBALANCER + 'Rebalancer_' + DISPATCHER + 'Dispatcher' + FILE_TYPE

        # fourcc = cv2.VideoWriter_fourcc(*'avc1')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(OUTPUT_NAME, fourcc, 60.0, VIDEO_RESOLUTION)
        # Draw frames and write to video
        for frame_coordinates in interpolated_vehicle_coordinates:
            # Create a blank image representing the map
            frame = np.zeros((VIDEO_RESOLUTION[1], VIDEO_RESOLUTION[0], 3), dtype=np.uint8)
            # Draw grid lines
            for i in range(1, GRID_SIZE[0]):
                cv2.line(frame, (i * (VIDEO_RESOLUTION[0] // GRID_SIZE[0]), 0), (i * (VIDEO_RESOLUTION[0] // GRID_SIZE[0]), VIDEO_RESOLUTION[1]), GRID_COLOR, 1)
            for i in range(1, GRID_SIZE[1]):
                cv2.line(frame, (0, i * (VIDEO_RESOLUTION[1] // GRID_SIZE[1])), (VIDEO_RESOLUTION[0], i * (VIDEO_RESOLUTION[1] // GRID_SIZE[1])), GRID_COLOR, 1)

            # Draw vehicles at their positions
            for vehicle_coordinate in frame_coordinates:
                cv2.circle(frame, tuple(vehicle_coordinate), VEHICLE_SIZE, VEHICLE_COLOR, -1)

            # Write frame to video
            out.write(frame)

        # Release the VideoWriter
        out.release()
        