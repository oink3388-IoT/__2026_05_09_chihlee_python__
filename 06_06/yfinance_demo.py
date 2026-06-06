import yfinance as yf
import pandas as pd
import numpy as np

def predict_next_week_stock(symbol='2317.TW'):
    """
    簡單股價預測：使用技術指標 + 移動平均線
    僅供參考，不構成投資建議
    """
    
    print(f"=== {symbol} 鴻海 下週股價預估 ===")
    print("⚠️ 僅供參考，不構成投資建議\n")
    
    # 1. 下載最近 3 個月的歷史資料
    stock = yf.Ticker(symbol)
    data = stock.history(period="3mo")
    
    if len(data) == 0:
        print("無法獲取資料")
        return
    
    # 2. 計算技術指標
    print("=== 歷史資料統計 ===")
    print(f"最近收盤價：{data['Close'].iloc[-1]:.2f}")
    print(f"3 個月平均收盤價：{data['Close'].mean():.2f}")
    print(f"最高價：{data['High'].max():.2f}")
    print(f"最低價：{data['Low'].min():.2f}")
    
    # 3. 移動平均線 (MA)
    ma5 = data['Close'].rolling(window=5).mean()
    ma10 = data['Close'].rolling(window=10).mean()
    ma20 = data['Close'].rolling(window=20).mean()
    
    current_ma5 = ma5.iloc[-1]
    current_ma10 = ma10.iloc[-1]
    current_ma20 = ma20.iloc[-1]
    
    print("\n=== 移動平均線 ===")
    print(f"MA5 (5 日均線): {current_ma5:.2f}")
    print(f"MA10 (10 日均線): {current_ma10:.2f}")
    print(f"MA20 (20 日均線): {current_ma20:.2f}")
    
    # 4. RSI (相對強弱指標)
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    current_rsi = rsi.iloc[-1]
    
    print("\n=== RSI (相對強弱指標) ===")
    print(f"RSI: {current_rsi:.2f}")
    
    if current_rsi > 70:
        print("RSI > 70: 可能超買 (價格過高)")
    elif current_rsi < 30:
        print("RSI < 30: 可能超賣 (價格過低)")
    else:
        print("RSI 在正常範圍")
    
    # 5. MACD (指數移動平均收散度)
    ema_12 = data['Close'].rolling(window=12).mean()
    ema_26 = data['Close'].rolling(window=26).mean()
    macd = ema_12 - ema_26
    macd_signal = macd.rolling(window=9).mean()
    
    current_macd = macd.iloc[-1]
    current_macd_signal = macd_signal.iloc[-1]
    
    print("\n=== MACD ===")
    print(f"MACD: {current_macd:.2f}")
    print(f"MACD Signal: {current_macd_signal:.2f}")
    
    if current_macd > current_macd_signal:
        print("MACD > Signal: 多頭訊號")
    else:
        print("MACD < Signal: 空頭訊號")
    
    # 6. 簡單預測：使用移動平均趨勢
    print("\n=== 下週股價預測 (僅供參考) ===")
    
    # 計算最近 5 天的平均漲跌幅
    recent_changes = data['Close'].diff().iloc[-5:]
    avg_change = recent_changes.mean()
    
    # 預測下週目標價
    current_price = data['Close'].iloc[-1]
    predicted_price = current_price + (avg_change * 5)  # 5 天
    
    # 計算波動範圍
    volatility = data['Close'].rolling(window=5).std().iloc[-1]
    upper_bound = predicted_price + volatility
    lower_bound = predicted_price - volatility
    
    print(f"當前收盤價: {current_price:.2f}")
    print(f"預估下週目標價: {predicted_price:.2f}")
    # ✅ 修正：把 f(...) 改成 f"...")
    print(f"預估區間: {lower_bound:.2f} ~ {upper_bound:.2f}")
    
    # 7. 趨勢判斷
    print("\n=== 趨勢判斷 ===")
    if current_price > current_ma5 and current_price > current_ma10:
        print("短期趨勢：多頭 (價格在均線之上)")
    elif current_price < current_ma5 and current_price < current_ma10:
        print("短期趨勢：空頭 (價格在均線之下)")
    else:
        print("短期趨勢：震盪 (價格在均線之間)")
    
    # 8. 買賣建議 (僅供參考)
    print("\n=== 買賣建議 (僅供參考) ===")
    if current_rsi < 30 and current_price > current_ma20:
        print("短線買入訊號：RSI 超賣 + 价格在 20 日均線之上")
    elif current_rsi > 70 and current_price < current_ma20:
        print("短線賣出訊號：RSI 超買 + 價格在 20 日均線之下")
    else:
        print("建議持觀望態度")
    
    print("\n╔════════════════════════════════════════╗")
    print("║ ⚠️ 重要提醒：                           ║")
    print("║   • 此預測僅供參考，不構成投資建議      ║")
    print("║   • 股市有風險，投資需謹慎              ║")
    print("║   • 請自行評估風險，獨立判斷            ║")
    print("╚════════════════════════════════════════╝")
    
    return {
        'current_price': current_price,
        'predicted_price': predicted_price,
        'upper_bound': upper_bound,
        'lower_bound': lower_bound
    }


if __name__ == '__main__':
    # 分析 2317 鴻海
    result = predict_next_week_stock('2317.TW')