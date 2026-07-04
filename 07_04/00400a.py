import numpy as np
import pandas as pd
import yfinance as yf

# 1. 設定下載標的：00400A 以及作為大盤基準的 0050
tickers = ["00400A.TW", "0050.TW"]

# 00400A 於 2026 年初上市，我們抓取上市至今的所有日資料
df = yf.download(tickers, period="max", interval="1d")

# 提取收盤價並計算每日報酬率
close_df = df["Close"]
returns_df = close_df.pct_change().dropna()

# 假設無風險利率 (例如定存或短債) 換算日利率
rf_daily = 0.015 / 252

# --- 2. 投報與基礎風險分析 ---
report = {}
for ticker in tickers:
    # 累積總報酬率
    cum_return = (1 + returns_df[ticker]).prod() - 1

    # 年化波動度
    annual_vol = returns_df[ticker].std() * np.sqrt(252)

    # 最大回撤 (Max Drawdown)
    cum_prod = (1 + returns_df[ticker]).cumprod()
    running_max = cum_prod.cummax()
    drawdown = (cum_prod - running_max) / running_max
    max_dd = drawdown.min()

    report[ticker] = {
        "累積總報酬率": f"{cum_return:.2%}",
        "年化波動度": f"{annual_vol:.2%}",
        "最大回撤": f"{max_dd:.2%}",
    }

# --- 3. 經理人能力指標：Alpha 與 Beta 分析 ---
# 運用線性回歸，以 0050 為獨立變數 X，00400A 為應變數 Y
X = returns_df["0050.TW"]
Y = returns_df["00400A.TW"]

# 計算共變異數與變異數
covariance = Y.cov(X)
market_variance = X.var()

# Beta：對大盤的敏感度
beta = covariance / market_variance

# Alpha：經理人帶來的超額報酬 (年化)
# Alpha = Y_mean - (Rf + Beta * (X_mean - Rf))
alpha_daily = Y.mean() - (rf_daily + beta * (X.mean() - rf_daily))
alpha_annual = alpha_daily * 252

# 夏普值 (Sharpe Ratio)
sharpe_00400A = (Y.mean() - rf_daily) / Y.std() * np.sqrt(252)

# 統整到最終報告
final_report = pd.DataFrame(report).T
final_report.loc["00400A.TW", "Beta值 (大盤敏感度)"] = f"{beta:.2f}"
final_report.loc["00400A.TW", "年化超額報酬 (Alpha)"] = f"{alpha_annual:.2%}"
final_report.loc["00400A.TW", "夏普值 (Sharpe)"] = f"{sharpe_00400A:.2f}"

print("=== 00400A 投報風險分析報告 ===")
print(final_report.fillna("-"))