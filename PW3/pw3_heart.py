"""PW3 - Dataset 1: Heart disease (Cleveland). Sessions 1 & 2 (tasks 1-5) + bonus."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

# ---- 1. Load
df = pd.read_csv("heart.csv")
print("shape:", df.shape); print(df.head())
cols = ["age", "chol", "trestbps", "thalach"]
cont = df[cols]
print(cont.describe().round(2))

# ---- 2. Distributions
fig, ax = plt.subplots(2, 2, figsize=(10, 7))
for a, c in zip(ax.ravel(), cols):
    a.hist(df[c], bins=20, density=True, color="#4c72b0", edgecolor="white", alpha=.8)
    x = np.linspace(df[c].min(), df[c].max(), 200)
    a.plot(x, stats.norm.pdf(x, df[c].mean(), df[c].std()), "r--", label="normal fit")
    a.set_title(f"{c}  (skew={stats.skew(df[c]):.2f})"); a.set_xlabel(c); a.legend()
plt.tight_layout(); plt.savefig("distributions.png", dpi=150); plt.close()

# ---- 3. Normality: Q-Q plots + Shapiro-Wilk + skew / excess kurtosis
fig, ax = plt.subplots(2, 2, figsize=(10, 7))
verdict = {}
for a, c in zip(ax.ravel(), cols):
    stats.probplot(df[c], dist="norm", plot=a); a.set_title(f"Q-Q plot: {c}")
    W, p = stats.shapiro(df[c])
    verdict[c] = (W, p, stats.skew(df[c]), stats.kurtosis(df[c]))
    print(f"{c:9s} Shapiro W={W:.4f} p={p:.2e} skew={verdict[c][2]:.2f} exkurt={verdict[c][3]:.2f}")
plt.tight_layout(); plt.savefig("qqplots.png", dpi=150); plt.close()

# ---- 4. thalach: disease vs healthy
d = df[df.target == 1]["thalach"]; h = df[df.target == 0]["thalach"]
print(f"\nn disease={len(d)}, healthy={len(h)}")
print(f"Levene (equal var) p={stats.levene(d, h).pvalue:.3f}")
print("Shapiro per group:", {k: round(stats.shapiro(v).pvalue, 4) for k, v in [("disease", d), ("healthy", h)]})
t = stats.ttest_ind(d, h, equal_var=False)
u = stats.mannwhitneyu(d, h, alternative="two-sided")
sp = np.sqrt(((len(d)-1)*d.var()+(len(h)-1)*h.var())/(len(d)+len(h)-2))
print(f"Welch t={t.statistic:.2f} p={t.pvalue:.2e}; Mann-Whitney U={u.statistic:.0f} p={u.pvalue:.2e}; Cohen d={(d.mean()-h.mean())/sp:.2f}")

# means + uncertainty (SEM and 95% CI)
rows = []
for name, g in [("disease", d), ("healthy", h)]:
    sem = stats.sem(g); ci = stats.t.interval(0.95, len(g)-1, g.mean(), sem)
    rows.append((name, g.mean(), g.std(), sem, ci)); 
    print(f"{name}: mean={g.mean():.2f} sd={g.std():.2f} SEM={sem:.2f} 95%CI=({ci[0]:.1f},{ci[1]:.1f})")
fig, a = plt.subplots(figsize=(5, 5))
a.errorbar([r[0] for r in rows], [r[1] for r in rows], yerr=[1.96*r[3] for r in rows],
           fmt="o", capsize=8, ms=9, color="k")
a.set_ylabel("mean thalach (bpm)"); a.set_title("Mean max heart rate ± 95% CI"); a.set_xlim(-.5, 1.5)
plt.tight_layout(); plt.savefig("means_ci.png", dpi=150); plt.close()

# ---- 5. age vs thalach
r, pr = stats.pearsonr(df.age, df.thalach); rho, ps = stats.spearmanr(df.age, df.thalach)
print(f"\nPearson r={r:.3f} p={pr:.1e}; Spearman rho={rho:.3f} p={ps:.1e}")
m, b = np.polyfit(df.age, df.thalach, 1)
fig, a = plt.subplots(figsize=(6, 5))
a.scatter(df.age, df.thalach, c=df.target, cmap="coolwarm", alpha=.7, edgecolor="k", lw=.3)
x = np.array([df.age.min(), df.age.max()]); a.plot(x, m*x+b, "k--", label=f"fit: slope={m:.2f} bpm/yr, r={r:.2f}")
a.set_xlabel("age"); a.set_ylabel("thalach"); a.legend(); a.set_title("Age vs max heart rate")
plt.tight_layout(); plt.savefig("age_vs_thalach.png", dpi=150); plt.close()

# ---- Bonus: Shannon entropy of categorical columns
for c in ["target", "sex"]:
    p = df[c].value_counts(normalize=True)
    H = -(p*np.log2(p)).sum()
    print(f"\n{c}: proportions={p.round(3).to_dict()}  entropy={H:.3f} bits (max {np.log2(len(p)):.2f})")
