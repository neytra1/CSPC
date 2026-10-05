"""PW2 Lab B, Part 4: chemical equilibrium H2 + I2 <=> 2 HI."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import newton, minimize

K = 15.6


def k_imbalance(x):
    """Zero at equilibrium."""
    return (2 * x) ** 2 / ((1 - x) * (1 - x)) - K


# Way 1: root-finding with Newton
x_newton = newton(k_imbalance, 0.5)

# Way 2: minimise the squared imbalance with SLSQP
res = minimize(lambda x: k_imbalance(x[0]) ** 2, x0=0.5,
               method="SLSQP", bounds=[(0, 0.999)])
x_slsqp = res.x[0]

print(f"Newton: x = {x_newton:.4f}")
print(f"SLSQP : x = {x_slsqp:.4f}")

x_eq = x_newton
print("\nEquilibrium amounts (mol):")
print(f"H2 = {1 - x_eq:.3f}")
print(f"I2 = {1 - x_eq:.3f}")
print(f"HI = {2 * x_eq:.3f}")

# plot how the amounts change with x
x = np.linspace(0, 1, 200)
plt.plot(x, 1 - x, label="H2")
plt.plot(x, 1 - x, "--", label="I2")
plt.plot(x, 2 * x, label="HI")
plt.axvline(x_eq, color="black", linestyle=":", label=f"equilibrium x = {x_eq:.2f}")
plt.xlabel("Extent of reaction x")
plt.ylabel("Amount (mol)")
plt.title("H2 + I2 <=> 2 HI")
plt.legend()
plt.grid(True)
plt.savefig("equilibrium.png", dpi=150)