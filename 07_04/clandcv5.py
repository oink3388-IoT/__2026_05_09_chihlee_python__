import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 定義我們要分析的四大電子權值股（改用 Dictionary，方便後面畫圖與報表顯示中文名稱）
ticker_map = {
    "2330.TW": "台積電",
    "2303.TW": "聯電",
    "2454.TW": "聯發科",
    "2317.TW": "鴻海"
}
tickers = list(ticker_map.keys())

# 抓取過去一年的日資料
print("正在從 Yahoo Finance 下載資料...")
data = yf.download(tickers, period="1y", interval="1d")

# 舊版/新版 yfinance 處理 Close 欄位（取其收盤價）
# 新版 yfinance 在多檔標的時，Close 會是 multi-index，這裡直接提取
close_data = data['Close']

# 計算每日報酬率 (Daily Return)
returns_df = close_data.pct_change().dropna()

# 將欄位代碼（如 2330.TW）換成中文名稱，後續圖表與報表會更直觀
returns_df = returns_df.rename(columns=ticker_map)

print("\n--- 每日報酬率前五行 ---")
print(returns_df.head())

# 2. 計算共變異數與相關係數矩陣
cov_matrix = returns_df.cov()
corr_matrix = returns_df.corr()

print("\n--- 共變異數矩陣 (Covariance Matrix) ---")
print(cov_matrix)

print("\n--- 相關係數矩陣 (Correlation Matrix) ---")
print(corr_matrix)

# 3. 畫成視覺化熱圖 (Heatmap)
# 修正 matplotlib 顯示中文會變亂碼的問題
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS', 'SimHei'] 
plt.rcParams['axes.unicode_minus'] = False 

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f")
plt.title("電子四雄相關係數矩陣 (Stock Correlation Matrix)")
plt.tight_layout()
plt.show()

# 4. 進階個股風險報酬分析報告
# 假設無風險利率為 1.5% (0.015)
risk_free_rate = 0.015
analysis_report = {}

for name in ticker_map.values():
    # 年化報酬率 (以一年 252 個交易日計算)
    annual_return = returns_df[name].mean() * 252
    
    # 年化波動度 (標準差)
    annual_volatility = returns_df[name].std() * np.sqrt(252)
    
    # 夏普值 (每承受一單位總風險，換來多少超額報酬)
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
    
    # 最大回撤 (Max Drawdown)：從波峰到波谷的最大跌幅
    cumulative_returns = (1 + returns_df[name]).cumprod()
    running_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    analysis_report[name] = {
        "年化報酬率": f"{annual_return:.2%}",
        "年化波動度": f"{annual_volatility:.2%}",
        "夏普值": f"{sharpe_ratio:.2f}",
        "最大回撤": f"{max_drawdown:.2%}"
    }

# 轉成 DataFrame 讓報告更美觀
report_df = pd.DataFrame(analysis_report).T
print("\n--- 進階個股風險報酬分析報告 ---")
print(report_df)