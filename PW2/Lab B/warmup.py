"""
PW2 Lab B Part 2 -- three routes to a minimum.

Compare gradient descent, Newton, and SLSQP on two functions:
  2A: f(x) = (x-3)**2 + 1          (easy, one minimum at x=3)
  2B: g(x) = x**4 - 3*x**2 + x + 5 (harder, several stationary points)
Run:  python warmup.py
"""
import numpy as np
from scipy.optimize import newton, minimize

# ---------- 2A: easy convex function ----------
def f(x):
    return (x - 3) ** 2 + 1
def f1(x): 
    return 2 * (x - 3)
def f2(x):          
    return 2


def gradient_descent(fprime, x0, step=0.1, n_iter=200):
    x = x0
    for _ in range(n_iter):
        x = x - step * fprime(x)
    return x


print("=== 2A: f(x) = (x-3)^2 + 1, start x0 = 0 ===")
print("gradient descent:", gradient_descent(f1, 0))
print("newton          :", newton(f1, 0, fprime=f2))
print("SLSQP           :", minimize(lambda x: f(x[0]), x0=0, method="SLSQP").x[0])


# ---------- 2B: harder landscape ----------
def g(x):
    return x**4 - 3 * x**2 + x + 5
def g1(x):
    return 4 * x**3 - 6 * x + 1
def g2(x):
    return 12 * x**2 - 6


print("\n=== 2B: g(x) = x^4 - 3x^2 + x + 5 ===")
for x0 in (0, 2):
    gd = gradient_descent(g1, x0, step=0.01, n_iter=2000)
    nw = newton(g1, x0, fprime=g2)
    sl = minimize(lambda x: g(x[0]), x0=x0, method="SLSQP").x[0]

    kind = "minimum" if g2(nw) > 0 else "maximum"
    print(f"\nstart x0 = {x0}")
    print(f"gradient descent: x = {gd:.4f}, g = {g(gd):.4f}")
    print(f"newton          : x = {nw:.4f}, g = {g(nw):.4f}, g'' = {g2(nw):.2f} -> {kind}")
    print(f"SLSQP           : x = {sl:.4f}, g = {g(sl):.4f}")