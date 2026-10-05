# CSPC - Computer Science for Physics and Chemistry

My coursework repository. Each practical is under PW<n>/Lab <X>/.

## Setup

Create the environment for a given lab:

    conda env create -f PW<1>/Lab\ <A>/environment.yml
    conda activate cspc

---

## PW1 - Lab A: Reproducible Foundations

**What I built:**
- A reproducible conda environment (`cspc`, Python 3.11 + numpy + pytest) and a
  Git repository tracking a radioactive-decay simulation with automated tests.

**Speed comparison (loop vs NumPy):**
- loop    : 3.2982 s
- numpy   : 0.0003 s
- speed-up: 9493.1 x faster

**Tests:** all passing? yes

**Conclusion:**
- NumPy was massively faster than the plain Python loop, which showed me why
  vectorising code matters. I also learned how Git branching and
  pushing to GitHub works, and why averaging over many runs is needed when
  dealing with randomness.


## PW1 --- Lab B

**Data:** The observed counts decrease over time, following an exponential decay shape.

**Comparison:**

**Pipeline:** The Snakemake rule rebuilds figure.png from the CSV and plot.py, and only reruns when one of them has changed.


## PW2 Lab A: Motion from Tracking Data

- **Measured Mean Acceleration:** -9.81 m/s²
- **Noise Explanation:** Differentiation amplifies measurement noise because it computes differences over small time intervals, making double-differentiation highly sensitive to small fluctuations.
- **Integration Findings:** Integrating noisy acceleration back to position suppresses noise via accumulation, matching the original trajectory within < 1 metre.



---

## PW2 --- Lab B: Optimization in Chemistry

**What I built:**
- `warmup.py`, which compares three optimisation methods (gradient descent, Newton's method and SLSQP) on an easy function and on a harder one.

### Part 2: Three routes to a minimum

**2A: easy function f(x) = (x-3)^2 + 1 (start x0 = 0):**
- gradient descent: x = 3.0
- Newton: x = 3.0
- SLSQP: x = 3.0
- All three methods reach the same minimum. The problem is so easy that it hides the differences between the methods.

**2B: harder function g(x) = x^4 - 3x^2 + x + 5:**

| Start | Gradient descent | Newton | SLSQP |
|---|---|---|---|
| x0 = 0 | -1.30 (minimum) | 0.17 (g'' = -5.65, maximum) | -1.30 (minimum) |
| x0 = 2 | 1.13 (minimum) | 1.13 (g'' = 9.35, minimum) | -1.30 (minimum) |

**Do the methods agree?**
- On the easy function, yes. On g(x), no: the answer depends on the method and on the starting point.

**Did Newton land on a minimum?**
- Not always. Starting from x0 = 0, Newton converged to x = 0.17, which is a maximum because g'' is negative there. Newton solves g'(x) = 0, which finds any stationary point (minimum, maximum or saddle), so the sign of g'' must be checked.

**How did the starting point change the result?**
- g(x) has two minima. The global minimum is at x = -1.30 (g = 1.49) and a local minimum is at x = 1.13 (g = 3.93).
- Starting from x0 = 2, gradient descent and Newton got trapped in the local minimum at x = 1.13. Starting from x0 = 0, gradient descent went to the global minimum, while Newton landed on the maximum.

**Lesson:**
- On a simple convex problem the methods agree easily. On a complicated landscape, the starting point and the algorithm both matter, and the type of stationary point must be checked.

### Part 3: Reaction rate fit

- Fitted rate constant k = 0.262 (the expected value is about 0.25). The fitted curve passes through the noisy measured points. The small difference from 0.25 comes from the noise in the data, including the noise in the first point used as C0.


### Part 4: Chemical equilibrium
- Newton and SLSQP agree: x = 0.667
- Equilibrium amounts: H2 = 0.333 mol, I2 = 0.333 mol, HI = 1.333 mol

### Part 5 (bonus): Titration

- The pH curve jumps and its slope peaks at about 50 mL, which is the equivalence point.