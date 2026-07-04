import numpy as np
import pandas as pd
import yfinance as yf

# ==========================================
# 1. 設定追蹤標的與參數
# ==========================================
# 00400A (主動動能), 00929 (被動高股息), 0050 (大盤基準)
tickers = ["00400A.TW", "00929.TW", "0050.TW"]

print("正在下載最新歷史資料...")
# 抓取上市以來的日資料進行策略驗證
df = yf.download(tickers, period="max", interval="1d")
close_df = df["Close"].dropna()

# 設定移動平均線天數（20日線為強弱分水嶺）
ma_window = 20
target_annual_return_per_million = 150000  # 目標 15 萬


# ==========================================
# 2. 定義量化交易策略（均線動能防禦）
# ==========================================
def run_strategy(ticker_name):
    price = close_df[ticker_name]
    ma = price.rolling(window=ma_window).mean()

    # 每日報酬率
    daily_pct = price.pct_change()

    # 交易訊號：當日收盤價 > 20MA 則隔日「持有(1)」，否則「空手(0)」進行防禦
    # .shift(1) 代表我們依據昨天的收盤訊號，決定今天的部位
    signal = (price > ma).astype(int).shift(1).fillna(0)

    # 策略每日報酬 = 訊號(0或1) * 股票當日實際漲跌幅
    strategy_returns = daily_pct * signal

    # 計算累積報酬率
    cum_strategy = (1 + strategy_returns).cumprod() - 1
    cum_benchmark = (1 + daily_pct).cumprod() - 1

    # 計算年化報酬率 (以 252 個交易日換算)
    days = len(daily_pct)
    annual_strategy = (1 + cum_strategy.iloc[-1]) ** (252 / days) - 1
    annual_benchmark = (1 + cum_benchmark.iloc[-1]) ** (252 / days) - 1

    # 計算最大回撤 (Max Drawdown) - 評估防禦效果
    cum_prod = (1 + strategy_returns).cumprod()
    running_max = cum_prod.cummax()
    drawdown = (cum_prod - running_max) / running_max
    max_dd = drawdown.min()

    # 最新一天的訊號判斷
    latest_price = price.iloc[-1]
    latest_ma = ma.iloc[-1]
    current_signal = "【 買入 / 續抱 】" if latest_price > latest_ma else "【 賣出 / 空手防禦 】"

    return {
        "目前股價": f"{latest_price:.2f}",
        "20日均線": f"{latest_ma:.2f}",
        "實時操作訊號": current_signal,
        "策略年化報酬率": f"{annual_strategy:.2%}",
        "原本買進持有的年化報酬率": f"{annual_benchmark:.2%}",
        "策略最大回撤(風險)": f"{max_dd:.2%}",
        "每百萬預估年回收": f"約 {1000000 * annual_strategy / 10000:,.0f} 萬",
    }


# ==========================================
# 3. 執行分析並印出即時儀表板
# ==========================================
results = {}
for t in ["00400A.TW", "00929.TW"]:
    results[t] = run_strategy(t)

# 轉成 DataFrame 方便閱讀
dashboard = pd.DataFrame(results).T
print("\n" + "=" * 50)
print(" 💰 00400A / 00929 實時追蹤與防禦決策儀表板 💰")
print("=" * 50)
print(dashboard[["目前股價", "20日均線", "實時操作訊號", "每百萬預估年回收"]])

print("\n" + "=" * 50)
print(" 📊 策略績效與風險回測驗證 (是否達成15%目標？)")
print("=" * 50)
print(dashboard[["策略年化報酬率", "原本買進持有的年化報酬率", "策略最大回撤(風險)"]])