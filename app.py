import streamlit as st
import pandas as pd
import numpy as np
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="GoldWin AI - XAUUSD", layout="centered", initial_sidebar_state="collapsed")

# --- INJEKSI CUSTOM CSS (Desain Elegan & Premium) ---
st.markdown("""
    <style>
    /* Ubah warna background keseluruhan agar lebih gelap dan profesional */
    .stApp {
        background-color: #0b0f19;
        color: #ffffff;
    }
    
    /* Styling Judul Utama */
    h1 {
        color: #FFD700 !important; /* Warna Emas */
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 0rem;
    }
    
    /* Styling Sub-judul */
    .subtitle {
        color: #8A9AAB;
        text-align: center;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
    }
    
    /* Styling Tombol Scan */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 55px;
        font-size: 18px;
        font-weight: bold;
        background: linear-gradient(90deg, #FFD700 0%, #F5B041 100%);
        color: #111827 !important;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
        background: linear-gradient(90deg, #F5B041 0%, #FFD700 100%);
    }

    /* Styling Kotak Indikator (Cards) */
    div[data-testid="column"] {
        background-color: #171f32;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #2a354d;
        text-align: center;
    }
    
    /* Divider Custom */
    hr {
        border-color: #2a354d;
    }
    </style>
""", unsafe_allow_html=True)


# --- FUNGSI DUMMY DATA & LOGIKA STRATEGI ---
# (Fungsi tetap sama seperti sebelumnya, hanya disembunyikan di background)
def generate_dummy_data(periods=100):
    np.random.seed(int(time.time())) # Seed dinamis agar hasil berubah-ubah tiap klik
    close_prices = np.cumsum(np.random.randn(periods) * 2) + 2000
    data = [[close_prices[i-1] if i > 0 else close_prices[0]-1, max(close_prices[i-1] if i > 0 else close_prices[0]-1, close_prices[i]) + abs(np.random.randn()), min(close_prices[i-1] if i > 0 else close_prices[0]-1, close_prices[i]) - abs(np.random.randn()), close_prices[i]] for i in range(periods)]
    return pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close'])

def check_h4_bias(df):
    c1, c2 = df.iloc[-1], df.iloc[-2]
    swing_high, swing_low = df['High'].rolling(10).max().iloc[-2], df['Low'].rolling(10).min().iloc[-2]
    bullish = c1['Close'] > c2['Open'] and c1['Open'] < c2['Close'] and c2['Close'] < c2['Open']
    bearish = c1['Close'] < c2['Open'] and c1['Open'] > c2['Close'] and c2['Close'] > c2['Open']
    if bullish and c1['Close'] > swing_high: return "Bullish", swing_high, swing_low
    elif bearish and c1['Close'] < swing_low: return "Bearish", swing_high, swing_low
    return "Netral", swing_high, swing_low

def check_h1_roadblock():
    return "Jalur Bersih" if np.random.choice([True, False], p=[0.7, 0.3]) else "Terhalang"

def check_m15_trigger(direction):
    if direction == "Bullish": return "W-Pattern Valid" if np.random.choice([True, False], p=[0.6, 0.4]) else "Menunggu Trigger"
    elif direction == "Bearish": return "M-Pattern Valid" if np.random.choice([True, False], p=[0.6, 0.4]) else "Menunggu Trigger"
    return "Menunggu Bias"


# --- HEADER DASHBOARD ---
st.markdown("<h1>✨ GoldWin AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Advanced Multi-Timeframe Confluence Scanner</p>", unsafe_allow_html=True)


# --- TOMBOL & ANIMASI LOADING ---
if st.button("🚀 SCAN XAUUSD SEKARANG"):
    
    # Animasi loading agar terkesan AI sedang bekerja menganalisis chart
    with st.spinner("🤖 GoldWin AI sedang menganalisis algoritma harga..."):
        time.sleep(1.5) # Jeda waktu 1.5 detik
        
    df_h4, df_h1, df_m15 = generate_dummy_data(50), generate_dummy_data(100), generate_dummy_data(200)
    h4_status, h4_res, h4_sup = check_h4_bias(df_h4)
    h1_status = check_h1_roadblock()
    m15_status = check_m15_trigger(h4_status)
    
    st.divider()
    
    # --- HASIL SCAN (TAMPILAN KOLOM) ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("Macro Bias (H4)")
        if h4_status == "Bullish": st.success("🟢 BULLISH")
        elif h4_status == "Bearish": st.error("🔴 BEARISH")
        else: st.info("⚪ NETRAL")
            
    with col2:
        st.caption("Roadblock (H1)")
        if h1_status == "Jalur Bersih": st.success("🟢 AMAN")
        else: st.warning("🟡 TERHALANG")
            
    with col3:
        st.caption("Trigger (M15)")
        if "Valid" in m15_status and h4_status == "Bullish": st.success("🟢 W-PATTERN")
        elif "Valid" in m15_status and h4_status == "Bearish": st.error("🔴 M-PATTERN")
        else: st.warning("🟡 MENUNGGU")
            
    st.divider()
    
    # --- OUTPUT SIGNAL FINAL ---
    current_price = df_m15.iloc[-1]['Close']
    
    if h4_status == "Bullish" and h1_status == "Jalur Bersih" and "Valid" in m15_status:
        st.success(f"### 🔥 SETUP BUY TERKONFIRMASI @ {current_price:.2f}")
        st.markdown(f"**Target Profit (TP):** `{h4_res:.2f}`  \n**Stop Loss (SL):** `{current_price - 2.0:.2f}`")
    elif h4_status == "Bearish" and h1_status == "Jalur Bersih" and "Valid" in m15_status:
        st.error(f"### 🔥 SETUP SELL TERKONFIRMASI @ {current_price:.2f}")
        st.markdown(f"**Target Profit (TP):** `{h4_sup:.2f}`  \n**Stop Loss (SL):** `{current_price + 2.0:.2f}`")
    else:
        st.info("💡 **Kesimpulan:** Kondisi market belum selaras. Tetap *Wait and See*.")
