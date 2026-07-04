import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
x = np.arange(1, 21)

y_pos = 2 * x + np.random.normal(0, 4, size=len(x))     # 正相關
y_neg = -2 * x + np.random.normal(0, 4, size=len(x))    # 負相關
y_none = np.random.normal(0, 10, size=len(x))           # 幾乎無相關

datasets = [
    ("Positive correlation", y_pos),
    ("Negative correlation", y_neg),
    ("No clear correlation", y_none)
]

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for ax, (title, y) in zip(axes, datasets):
    cov = np.cov(x, y)[0, 1]
    corr = np.corrcoef(x, y)[0, 1]
    ax.scatter(x, y, s=50)
    ax.set_title(f"{title}\nCov = {cov:.2f}, Corr = {corr:.2f}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()