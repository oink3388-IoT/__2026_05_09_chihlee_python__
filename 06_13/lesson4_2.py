import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import font_manager

# ====== 1. 讀取資料 ======
df = pd.read_csv("考試分數_3年6班.csv")

subjects = ['語文', '數學', '英語', '物理', '化學']
df['總分'] = df[subjects].sum(axis=1)
df['平均'] = df[subjects].mean(axis=1)

# ====== 2. 設定中文字體 ======
font_path = r"C:\Windows\Fonts\msjh.ttc"  # 微軟正黑體
if os.path.exists(font_path):
    font_manager.fontManager.addfont(font_path)
    font_name = font_manager.FontProperties(fname=font_path).get_name()
else:
    font_name = "Microsoft YaHei"

matplotlib.rcParams['font.family'] = font_name
matplotlib.rcParams['axes.unicode_minus'] = False

# ====== 3. 建立主視窗 ======
root = tk.Tk()
root.title("學生成績檢視器")
root.geometry("1000x600")
root.minsize(900, 550)

# ====== 4. 上方控制區 ======
top_frame = ttk.Frame(root, padding=10)
top_frame.pack(side=tk.TOP, fill=tk.X)

ttk.Label(top_frame, text="請選擇學生姓名：").pack(side=tk.LEFT)

student_var = tk.StringVar()
student_combo = ttk.Combobox(
    top_frame,
    textvariable=student_var,
    values=df['學生姓名'].tolist(),
    state="readonly",
    width=12
)
student_combo.pack(side=tk.LEFT, padx=8)
student_combo.current(0)

sum_var = tk.StringVar()
avg_var = tk.StringVar()

ttk.Label(top_frame, textvariable=sum_var, foreground="blue").pack(side=tk.LEFT, padx=20)
ttk.Label(top_frame, textvariable=avg_var, foreground="blue").pack(side=tk.LEFT, padx=10)

# ====== 5. 左右主區塊 ======
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

left_frame = ttk.LabelFrame(main_frame, text="分數明細", padding=10)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

right_frame = ttk.LabelFrame(main_frame, text="成績圖表", padding=10)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# ====== 6. 左側表格 ======
tree = ttk.Treeview(left_frame, columns=("科目", "分數"), show="headings", height=15)
tree.heading("科目", text="科目")
tree.heading("分數", text="分數")
tree.column("科目", width=100, anchor="center")
tree.column("分數", width=80, anchor="center")
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# ====== 7. 右側圖表 ======
fig = Figure(figsize=(6.5, 4.8), dpi=100)
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# ====== 8. 更新畫面函式 ======
def update_view(event=None):
    name = student_var.get()
    row = df[df['學生姓名'] == name].iloc[0]

    total = int(row['總分'])
    avg = round(row['平均'], 1)

    sum_var.set(f"總分：{total}")
    avg_var.set(f"平均：{avg}")

    # 更新左表
    for item in tree.get_children():
        tree.delete(item)

    for s in subjects:
        tree.insert("", tk.END, values=(s, int(row[s])))

    # 更新右圖
    ax.clear()
    scores = [int(row[s]) for s in subjects]
    bars = ax.bar(subjects, scores, color=["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f"])

    ax.set_title(f"{name} 成績", fontsize=16, fontweight="bold")
    ax.set_xlabel("科目")
    ax.set_ylabel("分數")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.3)

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            score + 1,
            str(score),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    canvas.draw()

student_combo.bind("<<ComboboxSelected>>", update_view)

# 初始顯示第一位學生
update_view()

root.mainloop()