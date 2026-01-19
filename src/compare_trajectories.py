import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# --- Project paths ---
project_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(project_dir, "..", "results")
plots_dir = os.path.join(results_dir, "plots")
data_dir = os.path.join(results_dir, "data")

# Create folders if they don't exist
os.makedirs(plots_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

# CSV paths
linear_csv = os.path.join(data_dir, "metrics_sweep.csv")
pid_csv = os.path.join(data_dir, "metrics_pid.csv")

# --- Check that CSVs exist ---
if not os.path.isfile(linear_csv):
    print(f"Error: Linear/Cubic CSV not found at {linear_csv}")
    sys.exit(1)
if not os.path.isfile(pid_csv):
    print(f"Error: PID CSV not found at {pid_csv}")
    sys.exit(1)

# --- Load data ---
df_lc = pd.read_csv(linear_csv)
df_pid = pd.read_csv(pid_csv)

# --- Choose a total_time and num_steps to compare ---
total_time = df_lc['Total Time'].unique()[0]
num_steps = df_lc['Num Steps'].unique()[0]

# --- Recreate time vector ---
time = np.linspace(0, total_time, num_steps)
theta_target = 90
theta_start = 0

# --- Trajectories ---
# Linear
theta_linear = theta_start + (theta_target - theta_start) * (time / total_time)
# Cubic
s = time / total_time
theta_cubic = theta_start + (theta_target - theta_start) * (3*s**2 - 2*s**3)
# PID
theta_pid = np.zeros(num_steps)
Kp = df_pid['Kp'].values[0]
Ki = df_pid['Ki'].values[0]
Kd = df_pid['Kd'].values[0]

integral = 0
prev_error = theta_target - theta_start
dt = total_time / num_steps

for i in range(1, num_steps):
    error = theta_target - theta_pid[i-1]
    integral += error * dt
    derivative = (error - prev_error) / dt
    control = Kp * error + Ki * integral + Kd * derivative
    theta_pid[i] = theta_pid[i-1] + control * dt
    prev_error = error

# --- Plot ---
plt.figure(figsize=(10,6))
plt.plot(time, theta_linear, label="Linear")
plt.plot(time, theta_cubic, label="Cubic")
plt.plot(time, theta_pid, label=f"PID (Kp={Kp}, Ki={Ki}, Kd={Kd})")
plt.axhline(theta_target, color='r', linestyle='--', label="Target")
plt.title(f"Joint Motion Comparison\nTotal Time={total_time}s, Steps={num_steps}")
plt.xlabel("Time (s)")
plt.ylabel("Joint Angle (degrees)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# --- Save plot ---
summary_plot_file = os.path.join(plots_dir, "comparison_linear_cubic_pid.png")
plt.savefig(summary_plot_file, dpi=300)
print(f"Plot saved to: {summary_plot_file}")

# --- Show plot ---
plt.show()  # Works in VS Code, Jupyter, or terminal