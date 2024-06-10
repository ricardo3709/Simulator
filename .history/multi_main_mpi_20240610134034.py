from mpi4py import MPI
import cProfile
from main import run_sim
import itertools

# MPI initialization
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Define variable values
REWARD_THETA = [
    0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1
]

def process_function(theta):
    run_sim(theta)

def distribute_tasks(thetas):
    # Distribute tasks evenly across available MPI ranks
    chunk_size = len(thetas) // size
    leftover = len(thetas) % size
    if rank < leftover:
        start = rank * (chunk_size + 1)
        end = start + chunk_size + 1
    else:
        start = rank * chunk_size + leftover
        end = start + chunk_size
    return thetas[start:end]

if __name__ == "__main__":
    # The number of times each theta should be processed
    repetitions = 5

    # Create a new list where each theta is repeated five times
    repeated_thetas = [(theta,) * repetitions for theta in REWARD_THETA]
    flat_list = [item for sublist in repeated_thetas for item in sublist]

    # Distribute tasks to each MPI rank
    assigned_thetas = distribute_tasks(flat_list)

    # Each process runs its assigned thetas
    for theta in assigned_thetas:
        process_function(theta)

    # Synchronize all MPI processes
    comm.Barrier()
    if rank == 0:
        print("Simulation completed on all ranks.")