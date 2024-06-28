from mpi4py import MPI
from main import run_sim

# MPI initialization
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def process_function():
    run_sim()

if __name__ == "__main__":
    # 每个进程运行一次main函数
    process_function()

    # 同步所有MPI进程
    comm.Barrier()
    if rank == 0:
        print("Simulation completed on all ranks.")