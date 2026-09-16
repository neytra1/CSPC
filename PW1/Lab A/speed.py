"""
Speed comparison: pure-Python loop vs vectorised NumPy.
Times both versions of the decay simulation on a large run.
"""

from time import perf_counter
from decay import simulate, simulate_loop

N0 = 200000
LAM = 0.4

# --- time the pure-Python loop version ---
start = perf_counter()
simulate_loop(N0, LAM)
loop_time = perf_counter() - start

# --- time the vectorised NumPy version ---
start = perf_counter()
simulate(N0, LAM)
numpy_time = perf_counter() - start

print(f"loop  : {loop_time:.4f} s")
print(f"numpy : {numpy_time:.4f} s")
print(f"speed-up: {loop_time / numpy_time:.1f} x faster")