import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr, spearmanr

# Load FINAL dataset (borough level)
df = pd.read_csv("data/cleaned/final_borough_dataset.csv")

print("Dataset preview:")
print(df.head())

df = df[df["gp_access"] >= 0]

# Correlation
x = df["imd_score"]
y = df["gp_access"]

pearson_r, pearson_p = pearsonr(x, y)
spearman_r, spearman_p = spearmanr(x, y)

print("\nPearson correlation:", pearson_r)
print("Pearson p-value:", pearson_p)

print("\nSpearman correlation:", spearman_r)
print("Spearman p-value:", spearman_p)

# Trendline
m, b = np.polyfit(x, y, 1)

plt.figure(figsize=(8,6))
plt.scatter(x, y)

# Labels
for _, row in df.iterrows():
    plt.annotate(
        row["borough"],
        (row["imd_score"], row["gp_access"]),
        fontsize=7
    )

# Line
plt.plot(x, m * x + b)

plt.xlabel("IMD Score (Higher = More Deprived)")
plt.ylabel("GP Access (%)")
plt.title(f"GP Access vs Deprivation\nPearson r = {pearson_r:.2f}")

plt.grid(True)
plt.tight_layout()

plt.savefig("data/cleaned/gp_vs_imd_trend.png")
plt.show()