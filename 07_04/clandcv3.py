import pandas as pd
import yfinance as yf

# 定義我們要分析的標的：台積電、聯發科、0050
tickers = ["2330.TW", "2454.TW", "0050.TW"]

# 抓取過去一年的日資料
data = yf.download(tickers, period="1y", interval="1d")

# 舊版/新版 yfinance 處理 Close 欄位（取其收盤價）
close_data = data['Close']

# 計算每日報酬率 (Daily Return)，這是做金融分析最關鍵的步驟！
# 因為我們分析的是「漲跌幅的連動」，而不是「股價絕對金額的連動」
returns_df = close_data.pct_change().dropna()

print("--- 每日報酬率前五行 ---")
print(returns_df.head())

import matplotlib.pyplot as plt
import seaborn as sns

# 1. 計算共變異數矩陣 (Covariance Matrix)
cov_matrix = returns_df.cov()
print("\n--- 共變異數矩陣 (Covariance Matrix) ---")
print(cov_matrix)

# 2. 計算相關係數矩陣 (Correlation Matrix)
corr_matrix = returns_df.corr()
print("\n--- 相關係數矩陣 (Correlation Matrix) ---")
print(corr_matrix)

# 3. 畫成視覺化熱圖 (Heatmap)，這是分析師報告中最常出現的圖
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f")
plt.title("Stock Correlation Matrix")
plt.show()

import numpy as np

# 假設無風險利率為 1.5% (0.015)
risk_free_rate = 0.015

analysis_report = {}

for ticker in tickers:
    # 年化報酬率 (以一年 252 個交易日計算)
    annual_return = returns_df[ticker].mean() * 252
    
    # 年化波動度 (標準差)
    annual_volatility = returns_df[ticker].std() * np.sqrt(252)
    
    # 夏普值 (每承受一單位總風險，換來多少超額報酬)
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
    
    # 最大回撤 (Max Drawdown)：從波峰到波谷的最大跌幅
    cumulative_returns = (1 + returns_df[ticker]).cumprod()
    running_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    analysis_report[ticker] = {
        "年化報酬率": f"{annual_return:.2%}",
        "年化波動度": f"{annual_volatility:.2%}",
        "夏普值": f"{sharpe_ratio:.2f}",
        "最大回撤": f"{max_drawdown:.2%}"
    }

# 轉成 DataFrame 讓報告更美觀
report_df = pd.DataFrame(analysis_report).T
print("\n--- 進階個股風險報酬分析報告 ---")
print(report_df)