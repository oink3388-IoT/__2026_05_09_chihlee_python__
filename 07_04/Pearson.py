import numpy as np
import matplotlib.pyplot as plt

x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
y = np.array([2, 4, 5, 4, 6, 7, 8, 9, 10, 12])

r = np.corrcoef(x, y)[0, 1]
print(f"Pearson r = {r:.3f}")

plt.scatter(x, y)
m, b = np.polyfit(x, y, 1)
plt.plot(x, m * x + b)
plt.title(f"Pearson r = {r:.3f}")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True, alpha=0.3)
plt.show()