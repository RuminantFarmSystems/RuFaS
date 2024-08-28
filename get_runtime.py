import json
import os

import numpy as np

logs_dir = "output/logs/"

logs_files = [log_file for log_file in os.listdir(logs_dir) if "logs" in log_file and "benchmark" in log_file]

run_times = []

for log_file in logs_files:
    with open(logs_dir + log_file) as log_fp:
        log_dict = json.load(log_fp)
        run_times.append(float(log_dict["SimulationEngine.simulate.total_simulation_time"]["values"][0].split(": ")[1]))

print(np.mean(run_times))
