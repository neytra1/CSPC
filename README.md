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

## PW3: Data, Distributions, Testing, and Causation

Scripts and plots are in `PW3/` (`pw3_heart.py`, `pw3_chemicals.py`). Run them from inside `PW3/`.

### Dataset 1: Heart disease (Cleveland)

**Source:** UCI Heart Disease dataset (Detrano et al., 1989), Cleveland subset, via Kaggle. 303 patients, `target` = 1 for heart disease (139) and 0 for healthy (164).

**Session 1: shape and normality** (`distributions.png`, `qqplots.png`)

| Variable | Shape | Shapiro p | Skew / ex. kurtosis | Verdict |
|---|---|---|---|---|
| age | one broad hump around 55-60, slightly left-skewed | 0.006 | -0.21 / -0.53 | approximately normal |
| chol | right-skewed with a long tail up to 564 | 6e-9 | 1.13 / 4.40 | not normal |
| trestbps | mildly right-skewed, tail up to 200 | 2e-6 | 0.70 / 0.85 | not normal (moderate) |
| thalach | mildly left-skewed, tail down to 71 | 7e-5 | -0.53 / -0.07 | roughly normal |

- With about 300 points, Shapiro-Wilk rejects even tiny deviations from normality, so I did not rely on the p-value alone. I also used Q-Q plots, skewness and kurtosis. `age` and `thalach` follow the Q-Q line closely, while `chol` and `trestbps` bend away at the tails.

**Session 2: is the effect real?**
- **Method:** I compared `thalach` between the two `target` groups with **Welch's t-test**, because the variances differ (Levene p = 0.023) and the disease group is normal while the healthy group is only mildly non-normal. With more than 100 patients per group the test is robust. I confirmed it with the non-parametric **Mann-Whitney U** test.
- **Result:** Welch t = -7.86, p = 9e-14. Mann-Whitney p = 2e-13. Cohen's d = -0.92 (large effect).
- **Conclusion:** The groups genuinely differ. Patients with heart disease reach a lower maximum heart rate, about 19 bpm lower.

**Uncertainty on the means** (`means_ci.png`)

| Group | Mean thalach | SEM | 95% CI |
|---|---|---|---|
| disease | 139.3 bpm | 1.92 | 135.5 to 143.0 |
| healthy | 158.4 bpm | 1.50 | 155.4 to 161.3 |

- The two confidence intervals do not overlap at all, so the plot agrees with the test.

**Age vs thalach** (`age_vs_thalach.png`)
- Pearson r = -0.39 (p = 1e-12), Spearman rho = -0.39, slope about -1 bpm per year. Older patients tend to have a lower maximum heart rate. The relationship is moderate with a lot of scatter, since age explains only about 15% of the variance.

**Bonus: how unpredictable is a category?**
- I used Shannon entropy, H = -sum(p log2 p).
- `target`: proportions 0.54 / 0.46, H = 0.995 bits out of a maximum of 1. It is almost perfectly balanced, so it is nearly as hard to guess as a coin flip.
- `sex`: proportions 0.68 / 0.32, H = 0.905 bits. It is more lopsided, so guessing "male" is right 68% of the time.

### Dataset 2: Chemical-exposure mystery

**Data note:** `chemicals cancer.csv` was not available on Moodle. I generated a synthetic stand-in with the same structure (1000 patients, benzene, cadmium, pollution index, age, malignancy score) using `make_standin_chemicals.py`. The numbers below come from that stand-in, not from the official file. The method is the same and can be re-run on the real file with `python pw3_chemicals.py`.

**Naive analysis (task 6)**
- Correlation with malignancy: benzene r = 0.72, cadmium r = 0.80.
- Taken at face value, **cadmium** looks like the cause because it is more strongly associated.

**Looking again (task 7)** (`confounding.png`)
- Suspected third variable: the pollution index. Cadmium correlates 0.96 with it, so cadmium may just be a stand-in for pollution.
- I restricted the data to patients with a similar pollution index (the 40th to 60th percentile, n = 199) and recomputed the correlations. I also computed partial correlations by removing the effect of pollution from both variables.

| | benzene | cadmium |
|---|---|---|
| Naive r | 0.72 | 0.80 |
| Restricted to similar pollution | 0.70 | 0.09 (p = 0.21) |
| Partial r (pollution removed) | 0.63 | 0.00 |

**Conclusion:** **Benzene is the real cause of malignancy.** Its association stays strong when pollution is held fixed. Cadmium only looked guilty: its association disappears once patients with the same pollution level are compared, because pollution drives both the cadmium level and the malignancy. This is a case where correlation is not causation.