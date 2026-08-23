import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime

# Настройка на уеб страницата
st.set_page_config(
    page_title="Pocket Option Pro Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Модерен Неонов CSS дизайн за уеб терминала - Напълно изчистен
st.markdown(
    "<style>"
    ".main { background-color: #0b0e14; }"
    "[data-testid='stSidebar'] { background-color: #11151f !important; border-right: 1px solid #1f2635; }"
    "div[data-testid='stMetric'] { background: #11151f !important; border: 1px solid #1f2635 !important; border-radius: 8px !important; padding: 8px 12px !important; box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important; margin-bottom: 0px !important; }"
    ".terminal-title { color: #ffffff; font-family: 'Arial', sans-serif; font-weight: 800; letter-spacing: 0.5px; margin: 0px !important; font-size: 18px !important; }"
    "div[data-testid='stMetricValue'] { font-family: 'Courier New', monospace !important; font-size: 16px !important; font-weight: bold !important; color: #e2e8f0 !important; }"
    "div[data-testid='stMetricLabel'] { font-size: 10px !important; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8 !important; }"
    ".block-container { padding-top: 0.25rem !important; padding-bottom: 0.25rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }"
    "div[data-testid='stHorizontalBlock'] { gap: 8px !important; }"
    ".stSelectbox, .stButton, .stNumberInput { margin-bottom: 0px !important; }"
    "</style>",
    unsafe_allow_html=True
)

# Списък с всички 38 OTC актива
all_otc_assets = [
    "AUD/CAD (OTC)", "AUD/CHF (OTC)", "AUD/JPY (OTC)", "AUD/NZD (OTC)", "AUD/USD (OTC)",
    "CAD/CHF (OTC)", "CAD/JPY (OTC)", "CHF/JPY (OTC)", "EUR/AUD (OTC)", "EUR/CAD (OTC)",
    "EUR/CHF (OTC)", "EUR/GBP (OTC)", "EUR/HUF (OTC)", "EUR/JPY (OTC)", "EUR/NZD (OTC)",
    "EUR/PLN (OTC)", "EUR/RUB (OTC)", "EUR/TRY (OTC)", "EUR/USD (OTC)", "GBP/AUD (OTC)",
    "GBP/CAD (OTC)", "GBP/CHF (OTC)", "GBP/JPY (OTC)", "GBP/NZD (OTC)", "GBP/USD (OTC)",
    "NZD/CAD (OTC)", "NZD/CHF (OTC)", "NZD/JPY (OTC)", "NZD/USD (OTC)", "SGD/JPY (OTC)",
    "USD/BRL (OTC)", "USD/CAD (OTC)", "USD/CHF (OTC)", "USD/CNH (OTC)", "USD/COP (OTC)",
    "USD/EGP (OTC)", "USD/HKD (OTC)", "USD/HUF (OTC)", "USD/INR (OTC)", "USD/JPY (OTC)",
    "USD/KRW (OTC)", "USD/MXN (OTC)", "USD/MYR (OTC)", "USD/PHP (OTC)", "USD/PLN (OTC)",
    "USD/RUB (OTC)", "USD/SAR (OTC)", "USD/SGD (OTC)", "USD/THB (OTC)", "USD/TRY (OTC)",
    "USD/ZAR (OTC)", "BTC/USD (OTC)", "ETH/USD (OTC)", "LTC/USD (OTC)", "XRP/USD (OTC)",
    "GOLD (OTC)", "SILVER (OTC)", "COPPER (OTC)", "BRENT CRUDE (OTC)", "NATURAL GAS (OTC)",
    "ALIBABA (OTC)", "ALPHABET/GOOGLE (OTC)", "AMAZON (OTC)", "APPLE (OTC)", 
    "BOEING (OTC)", "COCA-COLA (OTC)", "FACEBOOK/META (OTC)", "INTEL (OTC)", 
    "MICROSOFT (OTC)", "NETFLIX (OTC)", "NVIDIA (OTC)", "TESLA (OTC)", "VISA (OTC)"
]

@st.cache_data(ttl=600)
def generate_fresh_history(asset_name):
    if "BTC" in asset_name: base_price = 64500.00
    elif "ETH" in asset_name: base_price = 3450.00
    elif "GOLD" in asset_name: base_price = 2350.00
    elif "BRENT" in asset_name: base_price = 82.40
    elif "JPY" in asset_name: base_price = 145.25
    elif "RUB" in asset_name or "HUF" in asset_name: base_price = 91.50
    elif "TRY" in asset_name: base_price = 34.15
    elif "SGD" in asset_name or "CAD" in asset_name or "AUD" in asset_name: base_price = 1.35
    elif "CHF" in asset_name: base_price = 0.89
    elif any(x in asset_name for x in ["APPLE", "GOOGLE", "META", "NVIDIA", "NETFLIX", "TESLA", "MICROSOFT", "AMAZON", "VISA", "BOEING"]):
        base_price = random.uniform(120.00, 480.00)
    else: base_price = 1.1234
        
    history = []
    for _ in range(120):
        if base_price > 10000: step = 15.00
        elif base_price > 1000: step = 1.50
        elif base_price > 100: step = 0.20
        elif base_price > 10: step = 0.02
        else: step = 0.0003
        base_price += random.choice([-step, -step/2, step/2, step])
        history.append(round(base_price, 5))
    return history

# Инициализация на сесията
if "is_running" not in st.session_state: st.session_state.is_running = False
if "selected_asset" not in st.session_state: st.session_state.selected_asset = "EUR/USD (OTC)"
if "price_history" not in st.session_state: st.session_state.price_history = generate_fresh_history(st.session_state.selected_asset)
if "current_price" not in st.session_state: st.session_state.current_price = st.session_state.price_history[-1]
if "start_price" not in st.session_state: st.session_state.start_price = st.session_state.price_history[-1]
if "last_tick_time" not in st.session_state: st.session_state.last_tick_time = time.time()

def calculate_ema(prices, period):
    if len(prices) < period: return None
    sma = sum(prices[:period]) / period
    multiplier = 2 / (period + 1)
    ema = sma
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    return round(ema, 5)

# --- SIDEBAR НАСТРОЙКИ ---
st.sidebar.markdown("<h2 style='color:#ffffff; font-size:18px; font-weight:bold; margin-bottom:5px;'>⚙️ КОНФИГУРАЦИЯ</h2>", unsafe_allow_html=True)
timeframes = ["1 min", "2 min", "3 min", "5 min", "10 min"]
selected_tf = st.sidebar.selectbox("⏱️ Графичен Таймфрейм:", timeframes, disabled=st.session_state.is_running)

if selected_tf == "1 min": default_fast, default_mid, default_slow = 12, 26, 100
elif selected_tf == "2 min": default_fast, default_mid, default_slow = 9, 21, 50
elif selected_tf == "3 min": default_fast, default_mid, default_slow = 7, 14, 30
else: default_fast, default_mid, default_slow = 5, 13, 34

st.sidebar.markdown("<div style='margin-bottom:5px;'></div>", unsafe_allow_html=True)
fast_p = st.sidebar.number_input("⚡ Бърза EMA:", min_value=2, max_value=50, value=default_fast, disabled=st.session_state.is_running)
mid_p = st.sidebar.number_input("📊 Средна EMA:", min_value=5, max_value=100, value=default_mid, disabled=st.session_state.is_running)
slow_p = st.sidebar.number_input("🐢 Бавна EMA:", min_value=10, max_value=200, value=default_slow, disabled=st.session_state.is_running)

st.sidebar.markdown("<hr style='border-color:#232a38; margin: 10px 0;'>", unsafe_allow_html=True)

if not st.session_state.is_running:
    if st.sidebar.button("🚀 СТАРТИРАЙ АНАЛИЗА", use_container_width=True, type="primary"):
        st.session_state.is_running = True
        st.session_state.start_price = st.session_state.current_price
        st.session_state.last_tick_time = time.time()
        st.rerun()
else:
    if st.sidebar.button("🛑 СПРИ ТЕРМИНАЛА", use_container_width=True):
        st.session_state.is_running = False
        st.rerun()

# Изчисляване на времевия цикъл
tf_to_seconds = {"1 min": 60, "2 min": 120, "3 min": 180, "5 min": 300, "10 min": 600}
required_seconds = tf_to_seconds.get(selected_tf, 60)
elapsed_seconds = int(time.time() - st.session_state.last_tick_time)
remaining_seconds = max(0, required_seconds - elapsed_seconds)

if st.session_state.is_running and remaining_seconds == 0:
    tf_multiplier = {"1 min": 1.0, "2 min": 1.3, "3 min": 1.6, "5 min": 2.0, "10 min": 3.0}
    mult = tf_multiplier.get(selected_tf, 1.0)
    
    if "BTC" in st.session_state.selected_asset: step = 15.00 * mult
    elif "ETH" in st.session_state.selected_asset: step = 1.50 * mult
    elif "GOLD" in st.session_state.selected_asset: step = 0.50 * mult
    elif "TRY" in st.session_state.selected_asset: step = 0.01 * mult
    elif "JPY" in st.session_state.selected_asset: step = 0.02 * mult
    else: step = 0.0003 * mult
        
    change = random.choice([-step, -step/2, 0, step/2, step])
    st.session_state.current_price = round(st.session_state.current_price + change, 5)
    st.session_state.price_history.append(st.session_state.current_price)
    if len(st.session_state.price_history) > 120:
        st.session_state.price_history.pop(0)
    st.session_state.last_tick_time = time.time()
    remaining_seconds = required_seconds

# Пазарни изчисления за ЕМА
ema_fast = calculate_ema(st.session_state.price_history, fast_p)
ema_mid = calculate_ema(st.session_state.price_history, mid_p)
ema_slow = calculate_ema(st.session_state.price_history, slow_p)

# Прецизиране по предходна свещ
prices_list = list(st.session_state.price_history)
prev_candle_close = prices_list[-1] if len(prices_list) >= 1 else 0
prev_candle_open = prices_list[-2] if len(prices_list) >= 2 else 0
is_prev_candle_bullish = prev_candle_close > prev_candle_open
is_prev_candle_bearish = prev_candle_close < prev_candle_open

decision_text = "ИЗЧАКВАНЕ НА СИГНАЛ ⏳"
decision_color = "#94a3b8"
glow_effect = "rgba(148,163,184,0.12)"

if ema_fast and ema_mid and ema_slow:
    if (ema_fast > ema_mid > ema_slow) and is_prev_candle_bullish:
        decision_text = "КУПУВАЙ (CALL / HIGHER) 🟢"
        decision_color = "#2ebd85"
        glow_effect = "rgba(46,189,133,0.20)"
    elif (ema_fast < ema_mid < ema_slow) and is_prev_candle_bearish:
        decision_text = "ПРОДАВАЙ (PUT / LOWER) 🔴"
        decision_color = "#df294a"
        glow_effect = "rgba(223,41,74,0.20)"
    else:
        decision_text = "⚠️ НЕ ТЪРКУВАЙ! (Консолидация)"
        decision_color = "#ffa500"
        glow_effect = "rgba(255,165,0,0.12)"

# --- ГОРЕН РЕД: ИНФО И ЧАСОВНИК ЧРЕЗ JAVASCRIPT ---
top_c1, top_c2 = st.columns(2)
top_c1.markdown("<h1 class='terminal-title'>📈 POCKET OPTION LIVE TERMINAL</h1>", unsafe_allow_html=True)

# ФИКСИРАНО: Безопасен начин за инжектиране на JavaScript без вътрешни кавички, които бъркат Python
js_clock = (
    "<div id='live-clock' style='text-align: right; color: #38bdf8; font-family: monospace; font-size: 14px; font-weight: bold; padding-top: 2px;'>Зареждане...</div>"
    "<script>"
    "setInterval(function() {"
    "var n = new Date();"
    "var d = String(n.getDate()).padStart(2,'0');"
