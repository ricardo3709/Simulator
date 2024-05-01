
# start time of initialization
from src.utility.utility_functions import *
from src.simulator.Simulator_platform import Simulator_Platform
import cProfile
# from src.value_function.value_function import ValueFunction

system_time = 0.0
print(f"[INFO] Initializing the simulator (fleet_size = {FLEET_SIZE[0]}, capacity = {VEH_CAPACITY[0]})")


def run_sim():
    main_sim_results = []
    # 1. Run Simulation
    # 1.1. Initialize the simulator and print its configuration.
    print(f"[INFO] Running simulation using dispatcher: {DISPATCHER}")
    print(f"[INFO] Running simulation using fleet size: {FLEET_SIZE[0]}")
    print(f"[INFO] Running simulation using vehicle capacity: {VEH_CAPACITY[0]}")
    platform = Simulator_Platform(system_time)
    # 1.2. Run simulation. ("frames_system_states" is only recorded If RENDER_VIDEO is enabled, or it is None.)
    frames_system_states = platform.run_simulation()
    # 1.3. Output the simulation results.
    platform.create_report()



if __name__ == '__main__':
   cProfile.run("run_sim()",filename="30mins_result.out")



