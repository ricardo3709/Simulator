"""
constants are found here
"""
import pickle
import os
from dateutil.parser import parse

##################################################################################
# Data File Path
##################################################################################
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# MAP_NAME = "SmallGrid" 
MAP_NAME = "Manhattan"

# small-grid-data
PATH_SMALLGRID_ARCS = f"{ROOT_PATH}/SmallGridData/SmallGrid_Arcs.csv"
PATH_SMALLGRID_REQUESTS = f"{ROOT_PATH}/SmallGridData/SmallGrid_Requests.csv"
PATH_SMALLGRID_TIMECOST = f"{ROOT_PATH}/SmallGridData/SmallGrid_TimeCost.csv"
PATH_SMALLGRID_ALL_PATH_TABLE = f"{ROOT_PATH}/SmallGridData/SmallGrid_AllPathTable.pickle"
NUM_NODES_SMALLGRID = 100

# Manhattan-data
PATH_MANHATTAN_ALL_PATH_MATRIX = f"{ROOT_PATH}/NYC/NYC_Manhattan_AllPathMatrix.pickle"
PATH_MANHATTAN_ALL_PATH_TIME_MATRIX = f"{ROOT_PATH}/NYC/NYC_Manhattan_AllPathTimeMatrix.pickle"
PATH_MANHATTAN_REQUESTS = f"{ROOT_PATH}/NYC/NYC_Manhattan_Requests.csv"
NUM_NODES_MANHATTAN = 4091

##################################################################################
# Mod System Config
##################################################################################
# dispatch_config
DISPATCHER = "SBA"        # 3 options: SBA, OSP-NR, OSP
REBALANCER = "NJO"        # 3 options: NONE, NPO, NJO

# fleet_config:

# for small-grid-data
# FLEET_SIZE = [100]
# VEH_CAPACITY = [4]
# MAX_PICKUP_WAIT_TIME = 5 # 5 min
# MAX_DETOUR_TIME = 10 # 10 min

# for Manhattan-data
FLEET_SIZE = [2000]
VEH_CAPACITY = [6]

MAX_PICKUP_WAIT_TIME = 5*60 # 5 min
MAX_DETOUR_TIME = 10*60 # 10 min

##################################################################################
# Simulation Config
##################################################################################
DEBUG_PRINT = False

# for small-grid-data
# SIMULATION_DURATION = 60.0 #SmallGridData has 60 minutes of data
# TIME_STEP = 0.25 # 15 seconds
# COOL_DOWN_DURATION = 60.0 # 60 minutes
# PENALTY = 5.0 #penalty for ignoring a request

# for Manhattan-data
SIMULATION_DURATION = 300 # 60 minutes = 3600 seconds
TIME_STEP = 15 # 15 seconds
COOL_DOWN_DURATION = 0 # 20 minutes = 1200 seconds
PENALTY = 80.0 #penalty for ignoring a request

def config_change_fs(fs):
    global FLEET_SIZE
    FLEET_SIZE[0] = fs


def config_change_vc(vc):
    global VEH_CAPACITY
    VEH_CAPACITY[0] = vc