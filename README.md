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
- (write 2-3 sentences yourself: what worked, what you learned, any problems)