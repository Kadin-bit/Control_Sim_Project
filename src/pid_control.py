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

total_times = [2]         # seconds for PID simulation
num_steps_list = [100]    # steps for PID simulation

# --- PID gains (tune these) ---
Kp = float(input("Enter Kp: "))
Ki = float(input("Enter Ki: "))
Kd = float(input("Enter Kd: "))

# --- Metrics calculation ---
def calc_metrics(theta, time, target):
    overshoot = max(theta) - target
    final_error = target - theta[-1]
    within_target = np.where(np.abs(theta - target) <= 1)[0]
    settling_time = time[within_target[0]] if len(within_target) > 0 else np.nan
    return overshoot, settling_time, final_error

# --- Prepare CSV ---
csv_file = os.path.join(data_dir, "metrics_pid.csv")
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Total Time", "Num Steps", "Kp", "Ki", "Kd", "Overshoot", "Settling Time", "Final Error"])

    # --- Sweep ---
    for total_time in total_times:
        for num_steps in num_steps_list:
            dt = total_time / num_steps
            time = np.linspace(0, total_time, num_steps)
            theta = np.zeros(num_steps)
            
            # PID terms
            integral = 0
            prev_error = theta_target - theta_start
            
            for i in range(1, num_steps):
                error = theta_target - theta[i-1]
                integral += error * dt
                derivative = (error - prev_error) / dt
                control = Kp * error + Ki * integral + Kd * derivative
                theta[i] = theta[i-1] + control * dt  # simple Euler integration
                prev_error = error

            # Metrics
            overshoot, settling_time, final_error = calc_metrics(theta, time, theta_target)

            # Save to CSV
            writer.writerow([total_time, num_steps, Kp, Ki, Kd, overshoot, settling_time, final_error])

            # Plot
            plt.figure()
            plt.plot(time, theta, label=f"PID (Kp={Kp}, Ki={Ki}, Kd={Kd})")
            plt.axhline(theta_target, color='r', linestyle='--', label="Target")
            plt.xlabel("Time (s)")
            plt.ylabel("Joint Angle (degrees)")
            plt.title(f"PID Simulation: Total Time={total_time}s, Steps={num_steps}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            # Filename includes gains
            plot_filename = f"pid_Kp{Kp}_Ki{Ki}_Kd{Kd}_time{total_time}_steps{num_steps}.png"
            plt.savefig(os.path.join(plots_dir, plot_filename))
            
            # Show plot window
            plt.show()  # pops up the plot immediately

print("PID simulation complete. Metrics saved to:", csv_file)