"""
PW2 Lab A -- Motion from tracking data.

Read noisy free-fall position measurements, then:
  - differentiate once  -> velocity
  - differentiate twice -> acceleration (should be ~ constant -g, but noisy!)
  - integrate the acceleration back up -> recover velocity and position

Complete the TODOs. Run:  python analysis.py
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid

import numpy as np

data = np.loadtxt('freefall.csv', delimiter=',', skiprows=1)
t = data[:, 0]
y = data[:, 1]

v = np.gradient(y, t)
a = np.gradient(v, t)

mean_a = np.mean(a)
print(f"Mean Acceleration: {mean_a:.2f} m/s^2")

std_a = np.std(a)
print(f"Acceleration Standard Deviation: {std_a:.2f} m/s^2")

from scipy.integrate import cumulative_trapezoid

v_rec = cumulative_trapezoid(a, t, initial=0) + v[0]
y_rec = cumulative_trapezoid(v_rec, t, initial=0) + y[0]

max_diff = np.max(np.abs(y - y_rec))
print(f"Max difference in position: {max_diff:.4f} m")

import matplotlib.pyplot as plt

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

# Panel 1: Position
ax1.plot(t, y, label='Position (y)', color='blue')
ax1.set_ylabel('Position (m)')
ax1.grid(True)
ax1.legend()

# Panel 2: Velocity
ax2.plot(t, v, label='Velocity (v)', color='orange')
ax2.set_ylabel('Velocity (m/s)')
ax2.grid(True)
ax2.legend()

# Panel 3: Acceleration
ax3.plot(t, a, label='Acceleration (a)', color='red', alpha=0.7)
ax3.axhline(-9.81, color='black', linestyle='--', label='Theoretical g (-9.81 m/s²)')
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Acceleration (m/s²)')
ax3.grid(True)
ax3.legend()

plt.tight_layout()
plt.savefig('motion.png')