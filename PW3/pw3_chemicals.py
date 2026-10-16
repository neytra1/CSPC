"""PW3 - Dataset 2: chemical-exposure mystery. Needs chemicals_cancer.csv in this folder."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import glob

f = glob.glob("chemicals*cancer*.csv")[0]
df = pd.read_csv(f)
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
print(df.shape); print(df.head()); print(df.columns.tolist())
# adapt these if your column names differ:
BEN, CAD, POL, AGE = "benzene", "cadmium", "pollution_index", "age"
MAL = [c for c in df.columns if "malig" in c][0]

# ---- 6. Naive analysis
print("\nNAIVE correlations with", MAL)
for c in (BEN, CAD):
    r, p = stats.pearsonr(df[c], df[MAL]); print(f"  {c}: r={r:.3f} p={p:.1e}")
print("Correlation matrix:\n", df[[BEN, CAD, POL, AGE, MAL]].corr().round(3))

# ---- 7. Control for the confounder (pollution index)
lo, hi = df[POL].quantile([.4, .6])            # narrow slice around the median
sub = df[(df[POL] > lo) & (df[POL] < hi)]
print(f"\nRESTRICTED to {POL} in ({lo:.1f},{hi:.1f}), n={len(sub)}")
for c in (BEN, CAD):
    r, p = stats.pearsonr(sub[c], sub[MAL]); print(f"  {c}: r={r:.3f} p={p:.1e}")

# stricter check: partial correlation by regressing out the confounder
def resid(y, x): m, b = np.polyfit(x, y, 1); return y - (m*x + b)
for c in (BEN, CAD):
    r, p = stats.pearsonr(resid(df[c], df[POL]), resid(df[MAL], df[POL]))
    print(f"  partial r({c},{MAL}|{POL}) = {r:.3f} p={p:.1e}")

fig, ax = plt.subplots(2, 2, figsize=(10, 8))
for j, (d, tag) in enumerate([(df, "all patients"), (sub, "restricted pollution slice")]):
    for i, c in enumerate((BEN, CAD)):
        r = stats.pearsonr(d[c], d[MAL])[0]
        ax[j][i].scatter(d[c], d[MAL], s=8, alpha=.5); ax[j][i].set_title(f"{c} ({tag}) r={r:.2f}")
        ax[j][i].set_xlabel(c); ax[j][i].set_ylabel(MAL)
plt.tight_layout(); plt.savefig("confounding.png", dpi=150)
