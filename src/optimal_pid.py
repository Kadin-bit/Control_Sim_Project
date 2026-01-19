import numpy as np
import matplotlib.pyplot as plt
import os
import csv

# --- Project directories ---
# This makes paths relative to the script location and ensures folders exist
project_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(project_dir, "results")
plots_dir = os.path.join(results_dir, "plots")
data_dir = os.path.join(results_dir, "data")

os.makedirs(plots_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

# --- Experiment parameters ---
theta_start = 0
theta_target = 90
total_time = 2        # seconds
num_steps = 100       # steps
time = np.linspace(0, total_time, num_steps)
dt = total_time / num_steps

# --- PID gain ranges to test ---
Kp_range = [5, 6, 7]
Ki_range = [1.0, 1.2, 1.5]
Kd_range = [0.5, 0.6, 0.7]

# --- Metrics calculation ---
def calc_metrics(theta, time, target):
    overshoot = max(theta) - target
    final_error = target - theta[-1]
    within_target = np.where(np.abs(theta - target) <= 1)[0]
    settling_time = time[within_target[0]] if len(within_target) > 0 else np.nan
    return overshoot, settling_time, final_error

# --- Prepare CSV ---
csv_file = os.path.join(data_dir, "metrics_optimal_pid.csv")
best_cost = float("inf")
best_gains = (0, 0, 0)
best_theta = np.zeros(num_steps)

with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Kp", "Ki", "Kd", "Overshoot", "Settling Time", "Final Error", "Cost"])

    # --- Sweep all PID combinations ---
    for Kp in Kp_range:
        for Ki in Ki_range:
            for Kd in Kd_range:
                theta = np.zeros(num_steps)
                theta[0] = theta_start
                integral = 0
                prev_error = theta_target - theta_start

                # PID simulation
                for i in range(1, num_steps):
                    error = theta_target - theta[i-1]
                    integral += error * dt
                    derivative = (error - prev_error) / dt
                    control = Kp*error + Ki*integral + Kd*derivative
                    theta[i] = theta[i-1] + control*dt
                    prev_error = error

                overshoot, settling_time, final_error = calc_metrics(theta, time, theta_target)
                cost = settling_time + overshoot + abs(final_error)

                # ✅ Write metrics while file is open
                writer.writerow([Kp, Ki, Kd, overshoot, settling_time, final_error, cost])

                # Keep track of best PID
                if cost < best_cost:
                    best_cost = cost
                    best_gains = (Kp, Ki, Kd)
                    best_theta = theta.copy()

            # Keep track of best
            if cost < best_cost:
                best_cost = cost
                best_gains = (Kp, Ki, Kd)
                best_theta = theta.copy()

print("Optimal PID gains found:", best_gains)
overshoot, settling_time, final_error = calc_metrics(best_theta, time, theta_target)
print(f"Metrics - Overshoot: {overshoot:.2f}, Settling Time: {settling_time:.2f}, Final Error: {final_error:.2f}")

# --- Plot comparison with Linear & Cubic ---
theta_linear = theta_start + (theta_target - theta_start) * (time / total_time)
s = time / total_time
theta_cubic = theta_start + (theta_target - theta_start) * (3*s**2 - 2*s**3)

plt.figure()
plt.plot(time, theta_linear, label="Linear")
plt.plot(time, theta_cubic, label="Cubic")
plt.plot(time, best_theta, label=f"PID Optimized Kp={best_gains[0]}, Ki={best_gains[1]}, Kd={best_gains[2]}")
plt.axhline(theta_target, color='r', linestyle='--', label="Target")
plt.xlabel("Time (s)")
plt.ylabel("Joint Angle (°)")
plt.title("Linear vs Cubic vs Optimized PID")
plt.legend()
plt.grid(True)
plt.tight_layout()

plot_file = os.path.join(plots_dir, "comparison_optimal_pid.png")
plt.savefig(plot_file)
plt.show()

print("Comparison plot saved to:", plot_file)
print("Metrics CSV saved to:", csv_file)