import os
from ucimlrepo import fetch_ucirepo

concrete = fetch_ucirepo(id=165)          # 165 = Concrete Compressive Strength (Yeh, 1998)
X = concrete.data.features
y = concrete.data.targets

print(concrete.metadata)
print(concrete.variables)

X = X.copy()
X.columns = ["cement", "slag", "ash", "water", "superplastic",
             "coarse_agg", "fine_agg", "age"]
y = y.iloc[:, 0].rename("strength")

# check the new names match the original order
print(list(zip(concrete.data.features.columns, X.columns)))

os.makedirs("data", exist_ok=True)
X.assign(strength=y).to_csv("data/concrete.csv", index=False)
print("saved data/concrete.csv", X.shape)
