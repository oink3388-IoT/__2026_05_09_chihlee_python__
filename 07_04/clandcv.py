import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 產生示範資料
np.random.seed(42)
x = np.arange(1, 21)
y = 2 * x + np.random.normal(0, 4, size=len(x))

# 計算 covariance 與 correlation
cov_xy = np.cov(x, y)[0, 1]
corr_xy = np.corrcoef(x, y)[0, 1]

print("Covariance:", cov_xy)
print("Correlation:", corr_xy)

# 畫散點圖
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.scatter(x, y, color="steelblue")
plt.title(f"Scatter Plot\nCovariance = {cov_xy:.2f}")
plt.xlabel("x")
plt.ylabel("y")

plt.subplot(1, 2, 2)
plt.scatter(x, y, color="tomato")
plt.title(f"Scatter Plot\nCorrelation = {corr_xy:.2f}")
plt.xlabel("x")
plt.ylabel("y")

plt.tight_layout()
plt.show()