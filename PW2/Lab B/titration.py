"""PW2 Lab B, Part 5 (bonus): titration equivalence point."""
import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("titration.csv", delimiter=",", skiprows=1)
V = data[:, 0]
pH = data[:, 1]

slope = np.gradient(pH, V)       # d(pH)/dV
i = np.argmax(slope)             # index of the steepest point
V_eq = V[i]
print(f"Equivalence point: {V_eq:.1f} mL (pH = {pH[i]:.2f})")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
ax1.plot(V, pH, color="tab:blue")
ax1.axvline(V_eq, color="black", linestyle="--")
ax1.set_xlabel("Volume of base (mL)")
ax1.set_ylabel("pH")
ax1.set_title("Titration curve")
ax1.grid(True)

ax2.plot(V, slope, color="tab:red")
ax2.axvline(V_eq, color="black", linestyle="--", label=f"{V_eq:.1f} mL")
ax2.set_xlabel("Volume of base (mL)")
ax2.set_ylabel("Slope dpH/dV")
ax2.set_title("Slope peaks at equivalence")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig("titration.png", dpi=150)