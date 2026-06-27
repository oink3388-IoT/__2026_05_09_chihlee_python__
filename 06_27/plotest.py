import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Heiti TC', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

x = np.linspace(0, 4 * np.pi, 1000)

fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.25)

sin_line, = ax.plot(x, np.sin(x), lw=2, label="sin")
cos_line, = ax.plot(x, np.cos(x), lw=2, label="cos")

ax.set_xlim(0, 4 * np.pi)
ax.set_ylim(-5.5, 5.5)
ax.set_title("正弦 (sin) 與餘弦 (cos) 波形圖")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True)
ax.legend()

ax_A = plt.axes([0.15, 0.12, 0.7, 0.03])
ax_omega = plt.axes([0.15, 0.07, 0.7, 0.03])
ax_phi = plt.axes([0.15, 0.02, 0.7, 0.03])

slider_A = Slider(ax_A, "振幅 A", 0.1, 5.0, valinit=1.0)
slider_omega = Slider(ax_omega, "頻率 ω", 0.1, 10.0, valinit=1.0)
slider_phi = Slider(ax_phi, "相位 φ", 0, 2 * np.pi, valinit=0.0)

def update(val):
    A = slider_A.val
    omega = slider_omega.val
    phi = slider_phi.val
    sin_line.set_ydata(A * np.sin(omega * x + phi))
    cos_line.set_ydata(A * np.cos(omega * x + phi))
    ax.set_ylim(-A - 0.5, A + 0.5)
    fig.canvas.draw_idle()

slider_A.on_changed(update)
slider_omega.on_changed(update)
slider_phi.on_changed(update)

plt.show()