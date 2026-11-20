import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                      # no window: works inside Snakemake
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (mean_squared_error, mean_absolute_error, r2_score,
                             confusion_matrix, accuracy_score, precision_score,
                             recall_score, f1_score)
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.inspection import permutation_importance

os.makedirs("results", exist_ok=True)
os.makedirs("figures", exist_ok=True)
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

# ---- choices you make AFTER looking at the sweeps (edit, rerun) ----
K = 7                  # chosen number of neighbours (A6)
DEPTH = 4              # chosen tree depth (A6)
THRESHOLD = 0.5        # chosen decision threshold (A7)

def rmse(a, b):
    return np.sqrt(mean_squared_error(a, b))

def adj_r2(r2, n, p):
    # R2adj = 1 - (1-R2)(n-1)/(n-p-1)
    if n - p - 1 <= 0:
        return np.nan                      # undefined when p >= n-1
    return 1 - (1 - r2) * (n - 1) / (n - p - 1)

# ================= A2. Clean and look =================
df = pd.read_csv("data/concrete.csv")
print("\n=== A2 ===")
print("duplicate rows:", df.duplicated().sum())
print("missing values:\n", df.isna().sum())
df = df.drop_duplicates().reset_index(drop=True)
print("rows after cleaning:", len(df))
X = df.drop(columns="strength")
y = df["strength"]
print(df.describe().T)

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].scatter(df["cement"], df["strength"], s=8); ax[0].set_xlabel("cement (kg/m3)")
ax[1].scatter(df["age"], df["strength"], s=8);    ax[1].set_xlabel("age (days)")
for a in ax: a.set_ylabel("strength (MPa)")
plt.tight_layout(); plt.savefig("figures/A2_scatter.png", dpi=150); plt.close()

# ================= A3. Split =================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("\n=== A3 ===")
print("train:", X_train.shape, "test:", X_test.shape)

# ================= A4. Linear regression =================
print("\n=== A4 ===")
lin = LinearRegression().fit(X_train, y_train)
terms = " ".join(f"{c:+.4f}*{n}" for c, n in zip(lin.coef_, X.columns))
print(f"strength = {lin.intercept_:.3f} {terms}   [MPa]")
print(pd.Series(lin.coef_, index=X.columns, name="raw coef"))

ptr, pte = lin.predict(X_train), lin.predict(X_test)
n, p = len(X_train), X.shape[1]
r2_tr = r2_score(y_train, ptr)
tab4 = pd.DataFrame([{
    "train_RMSE": rmse(y_train, ptr), "test_RMSE": rmse(y_test, pte),
    "test_MAE": mean_absolute_error(y_test, pte), "train_R2": r2_tr,
    "train_adjR2": adj_r2(r2_tr, n, p), "test_R2": r2_score(y_test, pte)}])
print(tab4.round(3).to_string(index=False))

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(X_test["age"], y_test - pte, s=10)
ax.axhline(0, color="k"); ax.set_xscale("log")
ax.set_xlabel("age (days, log)"); ax.set_ylabel("residual = true - predicted (MPa)")
plt.tight_layout(); plt.savefig("figures/A4_residuals_age.png", dpi=150); plt.close()

# ================= A5. Polynomial regression =================
print("\n=== A5 ===")
rows = []
for d in [1, 2, 3, 4]:
    poly = make_pipeline(PolynomialFeatures(degree=d, include_bias=False),
                         StandardScaler(), LinearRegression())
    poly.fit(X_train, y_train)
    pf = poly[0].n_output_features_
    a, b = poly.predict(X_train), poly.predict(X_test)
    r2a = r2_score(y_train, a)
    rows.append({"degree": d, "p": pf, "train_RMSE": rmse(y_train, a),
                 "test_RMSE": rmse(y_test, b), "train_R2": r2a,
                 "train_adjR2": adj_r2(r2a, n, pf), "test_R2": r2_score(y_test, b)})
tab5 = pd.DataFrame(rows)
print(tab5.round(3).to_string(index=False))
print("training rows n =", n)

# ================= A6. Classification =================
print("\n=== A6 ===")
y_class = (df["strength"] >= 40).astype(int)
print(y_class.value_counts(normalize=True))
Xc_train, Xc_test, c_train, c_test = train_test_split(
    X, y_class, test_size=0.2, random_state=42, stratify=y_class)

# --- KNN sweep ---
Ks = [1, 3, 5, 7, 15, 25, 51, 101]
rows = []
for k in Ks:
    m = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k)).fit(Xc_train, c_train)
    rows.append({"K": k, "train_acc": m.score(Xc_train, c_train), "test_acc": m.score(Xc_test, c_test)})
knn_sweep = pd.DataFrame(rows)
print(knn_sweep.round(3).to_string(index=False))
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(knn_sweep["K"], knn_sweep["train_acc"], "o-", label="train")
ax.plot(knn_sweep["K"], knn_sweep["test_acc"], "s-", label="test")
ax.set_xscale("log"); ax.set_xlabel("K"); ax.set_ylabel("accuracy"); ax.legend()
plt.tight_layout(); plt.savefig("figures/A6_knn_sweep.png", dpi=150); plt.close()

knn = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=K)).fit(Xc_train, c_train)
knn_raw = KNeighborsClassifier(n_neighbors=K).fit(Xc_train, c_train)
print(f"\nK={K}: test acc WITH scaler = {knn.score(Xc_test, c_test):.3f}, "
      f"WITHOUT scaler = {knn_raw.score(Xc_test, c_test):.3f}")

accs = []
for rs in range(5):
    a_tr, a_te, b_tr, b_te = train_test_split(X, y_class, test_size=0.2, random_state=rs, stratify=y_class)
    mm = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=K)).fit(a_tr, b_tr)
    accs.append(mm.score(a_te, b_te))
print("5 splits test acc:", np.round(accs, 3), "mean=%.3f std=%.3f min-max spread=%.3f"
      % (np.mean(accs), np.std(accs), max(accs) - min(accs)))

# --- Tree sweep ---
rows = []
for dpt in [1, 2, 3, 4, 5, 6, 8, None]:
    t = DecisionTreeClassifier(criterion="entropy", max_depth=dpt, min_samples_leaf=1,
                               random_state=0).fit(Xc_train, c_train)
    rows.append({"max_depth": str(dpt), "leaves": t.get_n_leaves(),
                 "train_acc": t.score(Xc_train, c_train), "test_acc": t.score(Xc_test, c_test)})
tree_sweep = pd.DataFrame(rows)
print(tree_sweep.round(3).to_string(index=False))
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(tree_sweep["max_depth"], tree_sweep["train_acc"], "o-", label="train")
ax.plot(tree_sweep["max_depth"], tree_sweep["test_acc"], "s-", label="test")
ax.set_xlabel("max_depth"); ax.set_ylabel("accuracy"); ax.legend()
plt.tight_layout(); plt.savefig("figures/A6_tree_sweep.png", dpi=150); plt.close()

tree = DecisionTreeClassifier(criterion="entropy", max_depth=DEPTH, min_samples_leaf=1,
                              random_state=0).fit(Xc_train, c_train)
print(f"\nchosen tree: depth={tree.get_depth()}, leaves={tree.get_n_leaves()}")
print(export_text(tree, feature_names=list(X.columns), max_depth=2))

# ================= A7. Metrics =================
print("\n=== A7 ===")
def metrics_row(name, model):
    pred = model.predict(Xc_test)
    tn, fp, fn, tp = confusion_matrix(c_test, pred).ravel()
    return {"model": name, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "accuracy": accuracy_score(c_test, pred),
            "precision": precision_score(c_test, pred),
            "recall": recall_score(c_test, pred),
            "F1": f1_score(c_test, pred)}
metrics = pd.DataFrame([metrics_row(f"KNN (K={K})", knn),
                        metrics_row(f"Tree (depth={DEPTH})", tree)])
print(metrics.round(3).to_string(index=False))

# threshold study on the KNN (change to `tree` if you prefer)
proba = knn.predict_proba(Xc_test)[:, 1]
rows = []
for t in [0.3, 0.5, 0.7, 0.9]:
    pr = (proba >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(c_test, pr).ravel()
    rows.append({"threshold": t, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
                 "precision": precision_score(c_test, pr, zero_division=0),
                 "recall": recall_score(c_test, pr)})
thr = pd.DataFrame(rows)
print(thr.round(3).to_string(index=False))

# final table = chosen models + chosen threshold row
pr = (proba >= THRESHOLD).astype(int)
tn, fp, fn, tp = confusion_matrix(c_test, pr).ravel()
final = pd.concat([metrics, pd.DataFrame([{
    "model": f"KNN (K={K}) threshold={THRESHOLD}", "TP": tp, "FP": fp, "FN": fn, "TN": tn,
    "accuracy": accuracy_score(c_test, pr), "precision": precision_score(c_test, pr, zero_division=0),
    "recall": recall_score(c_test, pr), "F1": f1_score(c_test, pr)}])], ignore_index=True)
final.to_csv("results/A_metrics.csv", index=False)

# ================= A8. Feature importance =================
print("\n=== A8 ===")
pipe = make_pipeline(StandardScaler(), LinearRegression()).fit(X_train, y_train)
pi_knn = permutation_importance(knn, Xc_test, c_test, scoring="f1", n_repeats=20, random_state=0)
pi_tree = permutation_importance(tree, Xc_test, c_test, scoring="f1", n_repeats=20, random_state=0)
imp = pd.DataFrame({
    "raw_coef": lin.coef_,
    "std_coef": pipe[-1].coef_,
    "tree_importance": tree.feature_importances_,
    "perm_KNN": pi_knn.importances_mean,
    "perm_KNN_std": pi_knn.importances_std,
    "perm_tree": pi_tree.importances_mean,
    "perm_tree_std": pi_tree.importances_std}, index=X.columns)
print(imp.round(3))
print("\nranking raw |coef|:", list(imp["raw_coef"].abs().sort_values(ascending=False).index))
print("ranking std |coef|:", list(imp["std_coef"].abs().sort_values(ascending=False).index))
imp.to_csv("results/A_importance.csv")

fig, ax = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
imp["std_coef"].plot.barh(ax=ax[0], title="standardised coef (MPa per std)")
imp["tree_importance"].plot.barh(ax=ax[1], title="tree importance")
imp["perm_KNN"].plot.barh(ax=ax[2], xerr=imp["perm_KNN_std"], title="permutation (KNN, F1 drop)")
plt.tight_layout(); plt.savefig("figures/A8_importance.png", dpi=150); plt.close()

# ================= Bonus: physics features =================
print("\n=== Bonus ===")
def add_feats(D, wb=False):
    D = D.copy()
    D["age"] = np.log(D["age"])
    if wb:
        D["water"] = D["water"] / (D["cement"] + D["slag"] + D["ash"])
    return D
rows = []
for name, wb in [("log(age)", False), ("log(age) + w/b", True)]:
    m = LinearRegression().fit(add_feats(X_train, wb), y_train)
    rows.append({"model": name, "features": X.shape[1],
                 "test_R2": r2_score(y_test, m.predict(add_feats(X_test, wb)))})
print(pd.DataFrame(rows).round(3).to_string(index=False))
print("compare with the polynomial table (A5) above")
