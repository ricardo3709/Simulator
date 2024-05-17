from multiprocessing import Process, Manager
import cProfile
from main import run_sim

reward_thetas = [1.0, 1.5, 2.0]

def process_function(reward_theta, index):
    run_sim(reward_theta)
    # 你也可以将cProfile的调用放在这里，对每个进程单独进行性能分析
    cProfile.runctx("run_sim(reward_theta)", globals(), locals(), f"profile_output_{index}.out")

def multi_process_test():
    processes = []

    for i, theta in enumerate(reward_thetas):
        process = Process(target=process_function, args=(theta, i))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

if __name__ == "__main__":
    multi_process_test()