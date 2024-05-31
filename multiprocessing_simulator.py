from multiprocessing import Pool
import cProfile
from main import run_sim
import itertools

# Define variable values
REWARD_THETA = [
    0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 10.0, 20.0
]

def process_function(thetas):
    for theta in thetas:
        run_sim(theta)

def multi_process_test():
    # The number of times each theta should be processed
    repetitions = 4
    
    # Create a new list where each theta is repeated four times
    repeated_thetas = [(theta,) * repetitions for theta in REWARD_THETA]
    
    # Flatten the list to pass to Pool
    flat_list = [item for sublist in repeated_thetas for item in sublist]

    # Number of processes (should match the number of cores or your specific requirement)
    num_processes = 4
    
    # Split the flat list into chunks for each process
    # Ensure each process gets exactly one set of the repeated thetas
    theta_chunks = [flat_list[i::num_processes] for i in range(num_processes)]
    
    with Pool(num_processes) as pool:
        pool.map(process_function, theta_chunks)

if __name__ == "__main__":
    multi_process_test()
