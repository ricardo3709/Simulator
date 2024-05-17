# main.py
from src.simulator.Simulator_platform import Simulator_Platform
from src.simulator.config import ConfigManager  # Import the ConfigManager
import cProfile

def run_sim():
    config = ConfigManager()  # Instantiate the ConfigManager
    
    # Example: Modify configuration settings
    config.set('REWARD_THETA', 1.0)
    config.set('REWARD_TYPE', 'GEN')
    config.set('NODE_LAYERS', 2)
    config.set('MOVING_AVG_WINDOW', 20)

    # Use the configuration settings
    print(f"[INFO] Initializing the simulator")
    print(f"[INFO] Running simulation using dispatcher: {config.get('DISPATCHER')}")
    print(f"[INFO] Running simulation using fleet size: {config.get('FLEET_SIZE')[0]}")
    print(f"[INFO] Running simulation using vehicle capacity: {config.get('VEH_CAPACITY')[0]}")
    print(f"[INFO] Running simulation using rebalancer: {config.get('REBALANCER')}")
    print(f"[INFO] Running simulation with MAX_PICKUP_WAIT_TIME: {config.get('MAX_PICKUP_WAIT_TIME')} seconds")
    print(f"[INFO] Running simulation with MAX_DETOUR_TIME: {config.get('MAX_DETOUR_TIME')} seconds")
    print(f"[INFO] Running simulation with MAX_NUM_VEHICLES_TO_CONSIDER: {config.get('MAX_NUM_VEHICLES_TO_CONSIDER')}")
    print(f"[INFO] Running simulation with MAX_SCHEDULE_LENGTH: {config.get('MAX_SCHEDULE_LENGTH')}")
    print(f"[INFO] Running simulation with reward theta: {config.get('REWARD_THETA')}")

    system_initial_time = 0
    platform = Simulator_Platform(system_initial_time, config)
    platform.run_simulation()
    platform.create_report()

if __name__ == '__main__':
    run_sim()
