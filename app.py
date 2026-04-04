import streamlit as st
import pandas as pd
import numpy as np

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="XAUUSD Confluence Scanner", layout="wide")

# --- 1. FUNGSI DUMMY DATA ---
def generate_dummy_data(periods=100):
    """Menghasilkan data OHLC dummy untuk keperluan testing UI"""
    np.random.seed(42) # Seed agar hasil konsisten untuk testing
    close_prices = np.cumsum(np.random.randn(periods) * 2) + 2000 # Start sekitar harga Gold
    data = []
    for i in range(periods):
        open_p = close_prices[i-1] if i > 0 else close_prices[0] - 1
        close_p = close_prices[i]
        high_p = max(open_p, close_p) + abs(np.random.randn() * 2)
        low_p = min(open_p, close_p) - abs(np.random.randn() * 2)
        data.append([open_p, high_p, low_p, close_p])
    
    df = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close'])
    return df

# --- 2. FUNGSI LOGIKA STRATEGI ---
def check_h4_bias(df):
    """Cek Bias Makro di H4 (Engulfing + Breakout)"""
    if len(df) < 3: return "Netral", 0, 0
    
    c1, c2 = df.iloc[-1], df.iloc[-2]
    
    # Simple Engulfing Logic
    bullish_engulfing = c1['Close'] > c2['Open'] and c1['Open'] < c2['Close'] and c2['Close'] < c2['Open']
    bearish_engulfing = c1['Close'] < c2['Open'] and c1['Open'] > c2['Close'] and c2['Close'] > c2['Open']
    
    swing_high = df['High'].rolling(10).max().iloc[-2]
    swing_low = df['Low'].rolling(10).min().iloc[-2]
    
    if bullish_engulfing and c1['Close'] > swing_high:
        return "Bullish", swing_high, swing_low
    elif bearish_engulfing and c1['Close'] < swing_low:
        return "Bearish", swing_high, swing_low
    return "Netral", swing_high, swing_low

def check_h1_roadblock(df, direction):
    """Cek Hambatan di H1"""
    # Dummy logic: Simulasi roadblock clear dengan probabilitas acak untuk testing UI
    clear = np.random.choice([True, False], p=[0.7, 0.3]) 
    return "Jalur Bersih" if clear else "Terhalang"

def check_m15_trigger(df, direction):
    """Cek Trigger di M15 (W-Pattern / M-Pattern)"""
    # Dummy logic: Simulasi pattern terbentuk
    if direction == "Bullish":
        pattern_detected = np.random.choice([True, False], p=[0.6, 0.4])
        return "W-Pattern Valid" if pattern_detected else "Menunggu Trigger"
    elif direction == "Bearish":
        pattern_detected = np.random.choice([True, False], p=[0.6, 0.4])
        return "M-Pattern Valid" if pattern_detected else "Menunggu Trigger"
    return "Menunggu Bias"

# --- 3. UI DASHBOARD STREAMLIT ---
st.title("🎯 Multi-Timeframe Confluence Scanner: XAUUSD")
st.markdown("Algoritma Top-Down Analysis mendeteksi keselarasan arah antara H4, H1, dan trigger M15.")
st.divider()

if st.button("🔄 Scan Market Sekarang (Simulasi)"):
    # Generate Dummy Data
    df_h4 = generate_dummy_data(50)
    df_h1 = generate_dummy_data(100)
    df_m15 = generate_dummy_data(200)
    
    # Run Analysis
    h4_status, h4_res, h4_sup = check_h4_bias(df_h4)
    h1_status = check_h1_roadblock(df_h1, h4_status)
    m15_status = check_m15_trigger(df_m15, h4_status)
    
    # Display Status in Columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("H4 (Macro Bias)")
        if h4_status == "Bullish":
            st.success("🟢 BULLISH (Engulfing + Breakout)")
        elif h4_status == "Bearish":
            st.error("🔴 BEARISH (Engulfing + Breakout)")
        else:
            st.info("⚪ NETRAL")
            
    with col2:
        st.subheader("H1 (Roadblock)")
        if h1_status == "Jalur Bersih" and h4_status != "Netral":
            st.success(f"🟢 {h1_status}")
        else:
            st.warning(f"🟡 {h1_status}")
            
    with col3:
        st.subheader("M15 (Trigger)")
        if "Valid" in m15_status and h4_status == "Bullish":
            st.success(f"🟢 {m15_status}")
        elif "Valid" in m15_status and h4_status == "Bearish":
            st.error(f"🔴 {m15_status}")
        else:
            st.warning(f"🟡 {m15_status}")
            
    st.divider()
    
    # --- 4. SIGNAL OUTPUT & CALCULATION ---
    current_price = df_m15.iloc[-1]['Close']
    
    if h4_status == "Bullish" and h1_status == "Jalur Bersih" and "Valid" in m15_status:
        st.success(f"🔥 SETUP BUY XAUUSD TERKONFIRMASI PADA HARGA {current_price:.2f} 🔥")
        tp_price = h4_res # Target TP di Highest Resistance H4
        sl_price = current_price - 2.0 # SL simulasi 20 pips di bawah harga saat ini
        st.markdown(f"**Target Profit (TP):** `{tp_price:.2f}`")
        st.markdown(f"**Stop Loss (SL):** `{sl_price:.2f}`")
        
    elif h4_status == "Bearish" and h1_status == "Jalur Bersih" and "Valid" in m15_status:
        st.error(f"🔥 SETUP SELL XAUUSD TERKONFIRMASI PADA HARGA {current_price:.2f} 🔥")
        tp_price = h4_sup # Target TP di Lowest Support H4
        sl_price = current_price + 2.0 # SL simulasi 20 pips di atas harga saat ini
        st.markdown(f"**Target Profit (TP):** `{tp_price:.2f}`")
        st.markdown(f"**Stop Loss (SL):** `{sl_price:.2f}`")
        
    else:
        st.info("Menunggu semua konfirmasi timeframe selaras...")
else:
    st.write("Klik tombol di atas untuk memulai scanning.")
