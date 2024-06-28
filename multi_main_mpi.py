from mpi4py import MPI
from main import run_sim

# MPI initialization
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def process_function():
    args = {'REWARD_THETA': 5.0, 'REWARD_TYPE': 'REJ', 'NODE_LAYERS': 2, 'MOVING_AVG_WINDOW': 40, "TOGGLE_THETA_VALUE": 5.0}
    run_sim(args)

if __name__ == "__main__":
    # 每个进程运行一次main函数
    process_function()

    # 同步所有MPI进程
    comm.Barrier()
    if rank == 0:
        print("Simulation completed on all ranks.")