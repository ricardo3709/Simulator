
# start time of initialization
from src.utility.utility_functions import *
from src.simulator.Simulator_platform import Simulator_Platform
import cProfile
from src.simulator.config import *
# from src.value_function.value_function import ValueFunction

system_initial_time = 0
print(f"[INFO] Initializing the simulator")


def run_sim(reward_theta = REWARD_THETA):
    print(f"[INFO] Running simulation using dispatcher: {DISPATCHER}")
    print(f"[INFO] Running simulation using fleet size: {FLEET_SIZE[0]}")
    print(f"[INFO] Running simulation using vehicle capacity: {VEH_CAPACITY[0]}")
    print(f"[INFO] Running simulation using rebalancer: {REBALANCER}")
    print(f"[INFO] Running simulation with MAX_PICKUP_WAIT_TIME: {MAX_PICKUP_WAIT_TIME} seconds")
    print(f"[INFO] Running simulation with MAX_DETOUR_TIME: {MAX_DETOUR_TIME} seconds")
    print(f"[INFO] Running simulation with MAX_NUM_VEHICLES_TO_CONSIDER: {MAX_NUM_VEHICLES_TO_CONSIDER}")
    print(f"[INFO] Running simulation with MAX_SCHEDULE_LENGTH: {MAX_SCHEDULE_LENGTH}")
    print(f"[INFO] Running simulation with reward theta: {reward_theta}")
    platform = Simulator_Platform(system_initial_time)
    platform.run_simulation()
    platform.create_report()



if __name__ == '__main__':
   run_sim()



