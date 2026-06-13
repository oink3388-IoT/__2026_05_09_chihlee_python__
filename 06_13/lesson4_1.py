import pandas as pd
import os
import matplotlib
from matplotlib import font_manager
import shutil
import matplotlib.pyplot as plt

# ========== 步驟 1: 清除 matplotlib 字體快取 ==========
try:
    cache_dir = matplotlib.get_cachedir()
    shutil.rmtree(cache_dir, ignore_errors=True)
    print(f"✓ 已清除快取: {cache_dir}")
except:
    pass

# ========== 步驟 2: 註冊微軟正黑體 ==========
font_path = r'C:/Windows/Fonts/msjh.ttc'  # 微軟正黑體

if os.path.exists(font_path):
    font_manager.fontManager.addfont(font_path)
    font_prop = font_manager.FontProperties(fname=font_path)
    font_name = font_prop.get_name()
    
    # ========== 步驟 3: 設定 matplotlib 使用此字體 ==========
    matplotlib.rcParams['font.family'] = font_name
    matplotlib.rcParams['font.size'] = 12
    matplotlib.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False  # 顯示負號
    
    print(f"✓ 已設定中文字體: {font_name}")
else:
    print("✗ 未找到微軟正黑體，使用預設字體")
    matplotlib.rcParams['font.family'] = 'DejaVu Sans'

# ========== 步驟 4: 創建 output 目錄 ==========
os.makedirs('output', exist_ok=True)

# ========== 步驟 5: 讀取資料 ==========
df = pd.read_csv("考試分數_3年6班.csv")
print("\n=== 原始資料 ===")
print(df)

# ========== 步驟 6: 計算統計 ==========
subjects = ['語文', '數學', '英語', '物理', '化學']
subject_avg = df[subjects].mean()
df['總平均'] = df[subjects].mean(axis=1)

# ========== 步驟 7: 繪圖 1 - 各科平均比較 ==========
fig1, ax1 = plt.subplots(figsize=(10, 6))

ax1.plot(subjects, subject_avg, marker='o', linewidth=2, markersize=8, label='各科平均', color='blue')
ax1.fill_between(subjects, subject_avg, alpha=0.3, color='blue')

ax1.set_title('3 年 6 班 - 各科平均分數比較', fontsize=14, fontweight='bold')
ax1.set_xlabel('科目', fontsize=12)
ax1.set_ylabel('平均分數', fontsize=12)
ax1.set_ylim(60, 100)
ax1.grid(True, alpha=0.3)
ax1.legend()

plt.savefig('output/各科平均比較.png', dpi=300)
plt.close()
print("✓ 已保存: output/各科平均比較.png")

# ========== 步驟 8: 繪圖 2 - 前五名學生各科比較 ==========
top5 = df.nlargest(5, '總平均')

fig2, ax2 = plt.subplots(figsize=(12, 7))

colors = ['red', 'green', 'purple', 'orange', 'cyan']
for idx, (i, row) in enumerate(top5.iterrows()):
    ax2.plot(subjects, row[subjects], marker='o', linewidth=2, 
             markersize=6, label=row['學生姓名'], color=colors[idx])

ax2.set_title('3 年 6 班 - 前五名學生各科成績比較', fontsize=14, fontweight='bold')
ax2.set_xlabel('科目', fontsize=12)
ax2.set_ylabel('分數', fontsize=12)
ax2.set_ylim(60, 100)
ax2.grid(True, alpha=0.3)
ax2.legendfontsize = 10

plt.savefig('output/前五名學生各科比較.png', dpi=300)
plt.close()
print("✓ 已保存: output/前五名學生各科比較.png")

# ========== 步驟 9: 輸出統計資訊 ==========
print("\n=== 各科平均 ===")
print(subject_avg)

print("\n=== 前五名學生 ===")
print(df.nlargest(5, '總平均')[['學生姓名', '總平均']])

print("\n=== ✓ 完成！圖片已保存到 output/ 目錄 ===")