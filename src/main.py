import numpy as np
import matplotlib.pyplot as plt
import os
import csv

# --- Project directories ---
project_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(project_dir, "..", "results")
plots_dir = os.path.join(results_dir, "plots")
data_dir = os.path.join(results_dir, "data")

os.makedirs(plots_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

# --- Experiment parameters ---
theta_start = 0
theta_target = 90

total_times = [1, 2, 3]       # seconds
num_steps_list = [50, 100, 200]

# --- Metrics calculation ---
def calc_metrics(theta, time, target):
    overshoot = max(theta) - target
    final_error = target - theta[-1]
    within_target = np.where(np.abs(theta - target) <= 1)[0]
    settling_time = time[within_target[0]] if len(within_target) > 0 else np.nan
    return overshoot, settling_time, final_error

# --- Prepare CSV ---
csv_file = os.path.join(data_dir, "metrics_sweep.csv")
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Total Time", "Num Steps", "Method", "Overshoot", "Settling Time", "Final Error"])

    # --- Sweep ---
    for total_time in total_times:
        for num_steps in num_steps_list:
            time = np.linspace(0, total_time, num_steps)

            # Linear interpolation
            theta_linear = theta_start + (theta_target - theta_start) * (time / total_time)
            overshoot_linear, settling_linear, final_error_linear = calc_metrics(theta_linear, time, theta_target)

            # Cubic interpolation
            s = time / total_time
            theta_cubic = theta_start + (theta_target - theta_start) * (3*s**2 - 2*s**3)
            overshoot_cubic, settling_cubic, final_error_cubic = calc_metrics(theta_cubic, time, theta_target)

            # Save metrics to CSV
            writer.writerow([total_time, num_steps, "Linear", overshoot_linear, settling_linear, final_error_linear])
            writer.writerow([total_time, num_steps, "Cubic", overshoot_cubic, settling_cubic, final_error_cubic])

            # Save plot
            plt.figure()
            plt.plot(time, theta_linear, label="Linear")
            plt.plot(time, theta_cubic, label="Cubic")
            plt.xlabel("Time (s)")
            plt.ylabel("Joint Angle (degrees)")
            plt.title(f"Time={total_time}s, Steps={num_steps}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plot_filename = f"motion_time{total_time}_steps{num_steps}.png"
            plt.savefig(os.path.join(plots_dir, plot_filename))
            plt.close()  # close figure to avoid too many open plots

print("Parameter sweep complete. Metrics saved to:", csv_file)