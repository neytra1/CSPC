"""
PW2 Lab B Part 3 -- fit a reaction's rate constant to measured data.

A first-order reaction decays as  C(t) = C0 * exp(-k*t).  You have noisy
concentration-vs-time measurements; find the k that best matches them.
Complete the TODOs. Run:  python kinetics.py
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# 1. read the data (skip the header line)
data = np.loadtxt("kinetics.csv", delimiter=",", skiprows=1)
t = data[:, 0]
c = data[:, 1]

# 2. C0 is the first measured concentration
C0 = c[0]


# 3. total squared error between model and data
def error(k):
    k = k[0]                       # minimize passes k as an array
    model = C0 * np.exp(-k * t)
    return np.sum((c - model) ** 2)


# 4. minimise the error with SLSQP, k kept between 0 and 5
result = minimize(error, x0=0.5, method="SLSQP", bounds=[(0, 5)])
k_fit = result.x[0]
print(f"Fitted rate constant k = {k_fit:.4f}")
print(f"Remaining error        = {result.fun:.5f}")

# 5. plot data and fitted curve
t_smooth = np.linspace(t.min(), t.max(), 300)
plt.scatter(t, c, label="measured data", color="tab:blue")
plt.plot(t_smooth, C0 * np.exp(-k_fit * t_smooth), color="tab:red",
         label=f"fit: k = {k_fit:.3f}")
plt.xlabel("Time")
plt.ylabel("Concentration")
plt.title("First-order reaction: fitted rate constant")
plt.legend()
plt.grid(True)
plt.savefig("kinetics.png", dpi=150)