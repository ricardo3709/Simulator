from multiprocessing import Process, Manager
import cProfile
from main import run_sim

test_case_1 = []
test_case_2 = []
test_case_3 = []
test_case_4 = []

test_cases = [test_case_1, test_case_2, test_case_3, test_case_4]

def process_function(reward_theta, index):
    run_sim(test_cases)
    # cProfile.runctx("run_sim(reward_theta)", globals(), locals(), f"profile_output_{index}.out")

def multi_process_test():
    processes = []

    for i, test_case in enumerate(test_cases):
        process = Process(target=process_function, args=(test_case, i))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

if __name__ == "__main__":
    multi_process_test()