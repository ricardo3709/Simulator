
# start time of initialization
from src.utility.utility_functions import *
from src.simulator.Simulator_platform import Simulator_Platform
import cProfile
# from src.value_function.value_function import ValueFunction

system_time = 0.0
print(f"[INFO] Initializing the simulator (fleet_size = {FLEET_SIZE[0]}, capacity = {VEH_CAPACITY[0]})")


def run_sim():
    print(f"[INFO] Running simulation using dispatcher: {DISPATCHER}")
    print(f"[INFO] Running simulation using fleet size: {FLEET_SIZE[0]}")
    print(f"[INFO] Running simulation using vehicle capacity: {VEH_CAPACITY[0]}")
    platform = Simulator_Platform(system_time)
    platform.run_simulation()
    platform.create_report()



if __name__ == '__main__':
   cProfile.run("run_sim()",filename="60mins_may1.out")



