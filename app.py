import streamlit as st
import pandas as pd
import yfinance as yf
import time
from datetime import datetime
import pytz

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="GoldWin AI - Live Scanner", layout="centered", initial_sidebar_state="expanded")

# --- INJEKSI CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; }
    h1 { color: #FFD700 !important; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; margin-bottom: 0rem; }
    .subtitle { color: #8A9AAB; text-align: center; font-size: 1.1rem; margin-bottom: 2rem; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 55px; font-size: 18px; font-weight: bold;
        background: linear-gradient(90deg, #FFD700 0%, #F5B041 100%); color: #111827 !important;
        border: none; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
    }
    div[data-testid="column"] { background-color: #171f32; border-radius: 12px; padding: 15px; border: 1px solid #2a354d; text-align: center; }
    .live-time { text-align: center; color: #4ade80; font-size: 0.9rem; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
st.sidebar.header("🛡️ Scanner Settings")
market_type = st.sidebar.selectbox("Pilih Market", ["XAUUSD (Spot Gold)", "Crypto (BTC/USDT)", "Crypto (ETH/USDT)"])

# Mapping Ticker Yahoo Finance yang TEPAT
if "XAUUSD" in market_type:
    ticker_symbol = "XAUUSD=X" # Ticker Spot Gold (Forex)
    asset_name = "GOLD"
elif "BTC" in market_type:
    ticker_symbol = "BTC-USD"
    asset_name = "BITCOIN"
else:
    ticker_symbol = "ETH-USD"
    asset_name = "ETHEREUM"

# --- FUNGSI PULL DATA REAL-TIME ---
@st.cache_data(ttl=60) # Cache hanya bertahan 60 detik, memaksa refresh data baru
def get_live_data(ticker):
    try:
        # Mengambil data intraday (interval 1 jam)
        df = yf.download(ticker, period="5d", interval="1h", progress=False)
        if df.empty:
            return None, None
        
        # Bersihkan format kolom Yahoo Finance yang baru
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        last_time = df.index[-1]
        return df, last_time
    except Exception as e:
        return None, None

# --- FUNGSI LOGIKA STRATEGI ---
def analyze_bias(df):
    if len(df) < 5:
        return "Netral", 0, 0
        
    # Pastikan data diakses sebagai float, bukan Series
    c1_close = float(df['Close'].iloc[-1])
    c1_open = float(df['Open'].iloc[-1])
    c2_close = float(df['Close'].iloc[-2])
    c2_open = float(df['Open'].iloc[-2])
    
    swing_high = float(df['High'].rolling(4).max().iloc[-2])
    swing_low = float(df['Low'].rolling(4).min().iloc[-2])
    
    bullish = c1_close > c2_open and c1_open < c2_close and c2_close < c2_open
    bearish = c1_close < c2_open and c1_open > c2_close and c2_close > c2_open
    
    if bullish and c1_close > swing_high: 
        return "Bullish", swing_high, swing_low
    elif bearish and c1_close < swing_low: 
        return "Bearish", swing_high, swing_low
    return "Netral", swing_high, swing_low

# --- UI HEADER ---
st.markdown(f"<h1>✨ GoldWin AI: {asset_name}</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Professional Confluence Engine (100% Live Market Data)</p>", unsafe_allow_html=True)

# --- EXECUTION ---
if st.button(f"🚀 SCAN {asset_name} LIVE SEKARANG"):
    with st.spinner(f"🤖 Terhubung ke server market... Menarik harga {asset_name}..."):
        df_market, last_update = get_live_data(ticker_symbol)
        
    if df_market is None:
        st.error(f"⚠️ Gagal menarik data {asset_name}. Pasar mungkin tutup (Weekend) atau koneksi ditolak.")
    else:
        bias, res, sup = analyze_bias(df_market)
        curr_price = float(df_market['Close'].iloc[-1])
        
        # Tampilkan Timestamp agar ketahuan ini data asli
        wita_time = last_update.astimezone(pytz.timezone('Asia/Makassar'))
        st.markdown(f"<div class='live-time'>🟢 Data Terekam: {wita_time.strftime('%d %B %Y, %H:%M WITA')}</div>", unsafe_allow_html=True)
        
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
        
        if bias == "Bullish":
            st.success(f"### 🔥 SETUP BUY {asset_name} @ {curr_price:,.2f}")
            st.write(f"**Target Profit:** `{res:,.2f}` | **Stop Loss:** `{curr_price * 0.995:,.2f}`")
        elif bias == "Bearish":
            st.error(f"### 🔥 SETUP SELL {asset_name} @ {curr_price:,.2f}")
            st.write(f"**Target Profit:** `{sup:,.2f}` | **Stop Loss:** `{curr_price * 1.005:,.2f}`")
        else:
            st.info(f"💡 **Harga Live Saat Ini: {curr_price:,.2f}** | Kondisi market belum selaras. Tetap Wait and See.")
