import streamlit as st
import pandas as pd
import numpy as np
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="GoldWin AI - Pro Scanner", layout="centered", initial_sidebar_state="expanded")

# --- INJEKSI CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; }
    h1 { color: #FFD700 !important; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .subtitle { color: #8A9AAB; text-align: center; font-size: 1.1rem; margin-bottom: 2rem; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 55px; font-size: 18px; font-weight: bold;
        background: linear-gradient(90deg, #FFD700 0%, #F5B041 100%); color: #111827 !important;
        border: none; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
    }
    div[data-testid="column"] { background-color: #171f32; border-radius: 12px; padding: 15px; border: 1px solid #2a354d; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
st.sidebar.header("🛡️ Scanner Settings")
market_type = st.sidebar.selectbox("Pilih Market", ["XAUUSD (Gold)", "Crypto (BTC/USDT)", "Crypto (ETH/USDT)"])

# Menentukan harga dasar berdasarkan market yang dipilih
if "XAUUSD" in market_type:
    base_price = 2000
    asset_name = "GOLD"
elif "BTC" in market_type:
    base_price = 65000
    asset_name = "BITCOIN"
else:
    base_price = 3500
    asset_name = "ETHEREUM"

# --- FUNGSI DUMMY DATA & LOGIKA ---
def generate_market_data(base, periods=100):
    np.random.seed(int(time.time()))
    volatility = base * 0.005 # Volatilitas proporsional dengan harga aset
    close_prices = np.cumsum(np.random.randn(periods) * volatility) + base
    data = [[close_prices[i-1] if i > 0 else close_prices[0]-1, 
             max(close_prices[i-1] if i > 0 else close_prices[0]-1, close_prices[i]) + abs(np.random.randn() * (volatility/2)), 
             min(close_prices[i-1] if i > 0 else close_prices[0]-1, close_prices[i]) - abs(np.random.randn() * (volatility/2)), 
             close_prices[i]] for i in range(periods)]
    return pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close'])

def analyze_bias(df):
    c1, c2 = df.iloc[-1], df.iloc[-2]
    swing_high, swing_low = df['High'].rolling(10).max().iloc[-2], df['Low'].rolling(10).min().iloc[-2]
    bullish = c1['Close'] > c2['Open'] and c1['Open'] < c2['Close'] and c2['Close'] < c2['Open']
    bearish = c1['Close'] < c2['Open'] and c1['Open'] > c2['Close'] and c2['Close'] > c2['Open']
    if bullish and c1['Close'] > swing_high: return "Bullish", swing_high, swing_low
    elif bearish and c1['Close'] < swing_low: return "Bearish", swing_high, swing_low
    return "Netral", swing_high, swing_low

# --- UI HEADER ---
st.markdown(f"<h1>✨ GoldWin AI: {asset_name}</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Professional Crypto & Gold Confluence Engine</p>", unsafe_allow_html=True)

# --- EXECUTION ---
if st.button(f"🚀 SCAN {asset_name} SEKARANG"):
    with st.spinner(f"🤖 Membedah algoritma {asset_name}..."):
        time.sleep(1.5)
        
    df_h4 = generate_market_data(base_price, 50)
    bias, res, sup = analyze_bias(df_h4)
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("Macro Bias (H4)")
        if bias == "Bullish": st.success("🟢 BULLISH")
        elif bias == "Bearish": st.error("🔴 BEARISH")
        else: st.info("⚪ NETRAL")
    with col2:
        st.caption("Liquidity (H1)")
        st.success("🟢 CLEAR")
    with col3:
        st.caption("Trigger (M15)")
        st.warning("🟡 SCANNING")
            
    st.divider()
    curr = df_h4.iloc[-1]['Close']
    if bias == "Bullish":
        st.success(f"### 🔥 SETUP BUY {asset_name} @ {curr:.2f}")
        st.write(f"**Target Profit:** `{res:.2f}` | **Stop Loss:** `{curr * 0.98:.2f}`")
    elif bias == "Bearish":
        st.error(f"### 🔥 SETUP SELL {asset_name} @ {curr:.2f}")
        st.write(f"**Target Profit:** `{sup:.2f}` | **Stop Loss:** `{curr * 1.02:.2f}`")
    else:
        st.info("💡 Belum ada konfirmasi kuat. Tunggu sinyal berikutnya.")
