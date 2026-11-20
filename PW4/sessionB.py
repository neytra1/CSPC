import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline

os.makedirs("results", exist_ok=True)
os.makedirs("figures", exist_ok=True)
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

K_CHOSEN = 3           # choose after looking at the elbow (B4b)

# ================= B1 =================
wine = load_wine(as_frame=True)
X = wine.data
cultivar = wine.target
print("=== B1 ===")
print(wine.DESCR)
d = X.describe().T
print(d)
print("\nlargest std:\n", d["std"].sort_values(ascending=False).head(3))
print("smallest std:\n", d["std"].sort_values().head(3))

# ================= B2 =================
print("\n=== B2 ===")
pca_raw = PCA().fit(X)
print("explained variance ratio:", np.round(pca_raw.explained_variance_ratio_, 4))
print("PC1 loadings (sorted):\n",
      pd.Series(pca_raw.components_[0], index=X.columns).sort_values(key=abs, ascending=False))

# ================= B3 =================
print("\n=== B3 ===")
scaler = StandardScaler()
Z = scaler.fit_transform(X)
print("mean ~0:", np.round(Z.mean(axis=0), 6)[:4], "... std:", np.round(Z.std(axis=0), 3)[:4])
pca = PCA().fit(Z)
evr = pca.explained_variance_ratio_
cum = np.cumsum(evr)
print(pd.DataFrame({"PC": range(1, 14), "ratio": evr, "cumulative": cum}).round(4).to_string(index=False))
print("components for 90%:", int(np.argmax(cum >= 0.9)) + 1, "| PC1+PC2 keep:", round(cum[1], 4))

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(range(1, 14), evr, label="per component")
ax.plot(range(1, 14), cum, "o-", color="C1", label="cumulative")
ax.axhline(0.9, color="k", ls="--"); ax.set_xlabel("component"); ax.set_ylabel("variance ratio"); ax.legend()
plt.tight_layout(); plt.savefig("figures/B3_scree.png", dpi=150); plt.close()

load = pd.DataFrame(pca.components_[:2].T, index=X.columns, columns=["PC1", "PC2"])
print("\nPC1 loadings sorted:\n", load["PC1"].sort_values())
print("\nPC2 loadings sorted:\n", load["PC2"].sort_values())

scores = pca.transform(Z)
fig, ax = plt.subplots(figsize=(5, 5))
ax.scatter(scores[:, 0], scores[:, 1], s=15)
ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
plt.tight_layout(); plt.savefig("figures/B3_pc_plane.png", dpi=150); plt.close()

# ================= B4 =================
print("\n=== B4 ===")
print("(a) k=3, n_init=1:")
for rs in range(8):
    k1 = KMeans(n_clusters=3, init="k-means++", n_init=1, random_state=rs).fit(Z)
    print(f"  random_state={rs}  inertia={k1.inertia_:.3f}")
ks = range(1, 11)
inertias = [KMeans(n_clusters=k, n_init=10, random_state=0).fit(Z).inertia_ for k in ks]
print("(b) inertia vs k:", dict(zip(ks, np.round(inertias, 1))))
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(list(ks), inertias, "o-"); ax.set_xlabel("k"); ax.set_ylabel("inertia")
plt.tight_layout(); plt.savefig("figures/B4_elbow.png", dpi=150); plt.close()

# ================= B5 =================
print("\n=== B5 ===")
km = KMeans(n_clusters=K_CHOSEN, init="k-means++", n_init=10, max_iter=300, random_state=0).fit(Z)
print("cluster sizes:", np.bincount(km.labels_))
centres = pd.DataFrame(scaler.inverse_transform(km.cluster_centers_), columns=X.columns)
print(centres.round(2).T)
fig, ax = plt.subplots(figsize=(5, 5))
sc = ax.scatter(scores[:, 0], scores[:, 1], c=km.labels_, cmap="viridis", s=15)
ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
plt.tight_layout(); plt.savefig("figures/B5_clusters.png", dpi=150); plt.close()

# ================= B6 =================
print("\n=== B6 ===")
def agreement(labels):
    tab = pd.crosstab(cultivar, labels)
    return tab, tab.max(axis=0).sum() / len(cultivar)

versions = {
    "(i) scaled data": Z,
    "(ii) raw data": X.values,
    "(iii) PC1-PC2 of scaled": scores[:, :2],
}
rows = []
for name, data in versions.items():
    lab = KMeans(n_clusters=3, init="k-means++", n_init=10, random_state=0).fit_predict(data)
    tab, ag = agreement(lab)
    print(f"\n{name}\n{tab}\nagreement = {ag:.3f}")
    rows.append({"version": name, "agreement": ag})
pd.DataFrame(rows).to_csv("results/B_agreement.csv", index=False)

# ================= Bonus: what do labels buy you? =================
print("\n=== Bonus ===")
Xtr, Xte, ytr, yte = train_test_split(X, cultivar, test_size=0.25, random_state=42, stratify=cultivar)
m1 = make_pipeline(StandardScaler(), KNeighborsClassifier(5)).fit(Xtr, ytr)
m2 = make_pipeline(StandardScaler(), PCA(n_components=2), KNeighborsClassifier(5)).fit(Xtr, ytr)
print("KNN scaled, 13 features  test acc:", round(m1.score(Xte, yte), 3))
print("KNN scaled + PCA(2)      test acc:", round(m2.score(Xte, yte), 3))
