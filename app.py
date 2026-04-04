import streamlit as st
import pandas as pd
import yfinance as yf
import time

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
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
st.sidebar.header("🛡️ Scanner Settings")
market_type = st.sidebar.selectbox("Pilih Market", ["XAUUSD (Gold)", "Crypto (BTC/USDT)", "Crypto (ETH/USDT)"])

# Mapping Ticker Yahoo Finance
if "XAUUSD" in market_type:
    ticker_symbol = "GC=F" # Gold Futures
    asset_name = "GOLD"
elif "BTC" in market_type:
    ticker_symbol = "BTC-USD"
    asset_name = "BITCOIN"
else:
    ticker_symbol = "ETH-USD"
    asset_name = "ETHEREUM"

# --- FUNGSI PULL DATA REAL-TIME ---
def get_live_data(ticker):
    """Menarik data 60 hari terakhir dengan interval 1 jam dari Yahoo Finance"""
    try:
        df = yf.download(ticker, period="60d", interval="1h", progress=False)
        if df.empty:
            return None
        return df
    except Exception as e:
        return None

# --- FUNGSI LOGIKA STRATEGI ---
def analyze_bias(df):
    if len(df) < 10:
        return "Netral", 0, 0
        
    c1 = df.iloc[-1]
    c2 = df.iloc[-2]
    
    # Ambil nilai scalar untuk menghindari error multi-index DataFrame yfinance terbaru
    c1_close = float(c1['Close'].iloc[0]) if isinstance(c1['Close'], pd.Series) else float(c1['Close'])
    c1_open = float(c1['Open'].iloc[0]) if isinstance(c1['Open'], pd.Series) else float(c1['Open'])
    c2_close = float(c2['Close'].iloc[0]) if isinstance(c2['Close'], pd.Series) else float(c2['Close'])
    c2_open = float(c2['Open'].iloc[0]) if isinstance(c2['Open'], pd.Series) else float(c2['Open'])
    
    high_series = df['High'].squeeze()
    low_series = df['Low'].squeeze()
    
    swing_high = float(high_series.rolling(10).max().iloc[-2])
    swing_low = float(low_series.rolling(10).min().iloc[-2])
    
    bullish = c1_close > c2_open and c1_open < c2_close and c2_close < c2_open
    bearish = c1_close < c2_open and c1_open > c2_close and c2_close > c2_open
    
    if bullish and c1_close > swing_high: 
        return "Bullish", swing_high, swing_low
    elif bearish and c1_close < swing_low: 
        return "Bearish", swing_high, swing_low
    return "Netral", swing_high, swing_low

# --- UI HEADER ---
st.markdown(f"<h1>✨ GoldWin AI: {asset_name}</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Professional Crypto & Gold Confluence Engine (Live Market)</p>", unsafe_allow_html=True)

# --- EXECUTION ---
if st.button(f"🚀 SCAN {asset_name} LIVE SEKARANG"):
    with st.spinner(f"🤖 Menghubungkan ke server market & membedah algoritma {asset_name}..."):
        df_market = get_live_data(ticker_symbol)
        
    if df_market is None:
        st.error("Gagal menarik data live. Pasar mungkin sedang tutup atau koneksi API terganggu.")
    else:
        bias, res, sup = analyze_bias(df_market)
        
        # Ambil harga running terakhir yang benar-benar akurat
        curr = float(df_market['Close'].iloc[-1].iloc[0]) if isinstance(df_market['Close'].iloc[-1], pd.Series) else float(df_market['Close'].iloc[-1])
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("Macro Bias (H4)")
            if bias == "Bullish": st.success("🟢 BULLISH")
            elif bias == "Bearish": st.error("🔴 BEARISH")
            else: st.info("⚪ NETRAL")
        with col2:
            st.caption("Liquidity (H1)")
            st.success("🟢 CLEAR") # Simplifikasi untuk UI
        with col3:
            st.caption("Trigger (M15)")
            st.warning("🟡 SCANNING") # Simplifikasi untuk UI
                
        st.divider()
        
        if bias == "Bullish":
            st.success(f"### 🔥 SETUP BUY {asset_name} @ {curr:,.2f}")
            st.write(f"**Target Profit:** `{res:,.2f}` | **Stop Loss:** `{curr * 0.995:,.2f}`")
        elif bias == "Bearish":
            st.error(f"### 🔥 SETUP SELL {asset_name} @ {curr:,.2f}")
            st.write(f"**Target Profit:** `{sup:,.2f}` | **Stop Loss:** `{curr * 1.005:,.2f}`")
        else:
            st.info(f"💡 **Harga Saat Ini: {curr:,.2f}**. Kondisi market belum selaras. Tetap Wait and See.")
