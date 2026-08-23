import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime

# Настройка на уеб страницата
st.set_page_config(
    page_title="PO 3 EMA Bot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Компактни CSS стилове за събиране на всичко на 1 екран
st.markdown("""
    <style>
    .main { background-color: #1c1f26; }
    div[data-testid="stMetricValue"] { font-size: 20px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 12px !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    h1 { font-size: 24px !important; margin-bottom: 5px !important; }
    h5 { font-size: 14px !important; margin-top: 5px !important; margin-bottom: 5px !important; }
    </style>
""", unsafe_allow_html=True)

# Списък с всички 38 OTC актива
all_otc_assets = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "EUR/GBP (OTC)", "USD/CAD (OTC)", "NZD/USD (OTC)", "EUR/JPY (OTC)",
    "GBP/JPY (OTC)", "EUR/CAD (OTC)", "AUD/CAD (OTC)", "USD/CHF (OTC)",
    "EUR/CHF (OTC)", "CAD/JPY (OTC)", "AUD/JPY (OTC)", "CHF/JPY (OTC)",
    "GBP/CAD (OTC)", "EUR/AUD (OTC)", "NZD/JPY (OTC)", "AUD/NZD (OTC)",
    "GBP/CHF (OTC)", "EUR/NZD (OTC)", "GBP/AUD (OTC)", "USD/SGD (OTC)",
    "USD/TRY (OTC)", "EUR/TRY (OTC)", "NZD/CAD (OTC)", "AUD/CHF (OTC)",
    "GOLD (OTC)", "SILVER (OTC)", "APPLE (OTC)", "GOOGLE (OTC)",
    "MICROSOFT (OTC)", "AMAZON (OTC)", "TESLA (OTC)", "META (OTC)",
    "NVIDIA (OTC)", "NETFLIX (OTC)"
]

@st.cache_data(ttl=600)
def generate_fresh_history(asset_name):
    if "JPY" in asset_name: base_price = 145.25
    elif "TRY" in asset_name: base_price = 34.15
    elif "SGD" in asset_name: base_price = 1.34
    elif "CHF" in asset_name and "JPY" not in asset_name: base_price = 0.8950
    elif "GOLD" in asset_name: base_price = 2350.00
    elif "SILVER" in asset_name: base_price = 28.50
    elif any(x in asset_name for x in ["APPLE", "GOOGLE", "META", "NVIDIA", "NETFLIX", "TESLA", "MICROSOFT", "AMAZON"]):
        base_price = random.uniform(150.00, 450.00)
    else: base_price = 1.1234
        
    history = []
    for _ in range(120):
        if base_price > 1000: step = 0.50
        elif base_price > 100: step = 0.10
        elif base_price > 10: step = 0.01
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

# Страничен панел
st.sidebar.title("⚙ Настройки")
timeframes = ["1 min", "2 min", "3 min", "5 min", "10 min"]
selected_tf = st.sidebar.selectbox("⏱ Времева рамка:", timeframes, disabled=st.session_state.is_running)

if selected_tf == "1 min": default_fast, default_mid, default_slow = 12, 26, 100
elif selected_tf == "2 min": default_fast, default_mid, default_slow = 9, 21, 50
elif selected_tf == "3 min": default_fast, default_mid, default_slow = 7, 14, 30
else: default_fast, default_mid, default_slow = 5, 13, 34

fast_p = st.sidebar.number_input("Бърза EMA:", min_value=2, max_value=50, value=default_fast, disabled=st.session_state.is_running)
mid_p = st.sidebar.number_input("Средна EMA:", min_value=5, max_value=100, value=default_mid, disabled=st.session_state.is_running)
slow_p = st.sidebar.number_input("Бавна EMA:", min_value=10, max_value=200, value=default_slow, disabled=st.session_state.is_running)

if not st.session_state.is_running:
    if st.sidebar.button("🚀 СТАРТИРАЙ БОТ", use_container_width=True):
        st.session_state.is_running = True
        st.session_state.start_price = st.session_state.current_price
        st.session_state.last_tick_time = time.time()
        st.rerun()
else:
    if st.sidebar.button("🛑 СПРИ БОТ", use_container_width=True):
        st.session_state.is_running = False
        st.rerun()

# Изчисляване на времето
tf_to_seconds = {"1 min": 60, "2 min": 120, "3 min": 180, "5 min": 300, "10 min": 600}
required_seconds = tf_to_seconds.get(selected_tf, 60)
elapsed_seconds = int(time.time() - st.session_state.last_tick_time)
remaining_seconds = max(0, required_seconds - elapsed_seconds)

if st.session_state.is_running and remaining_seconds == 0:
    tf_multiplier = {"1 min": 1.0, "2 min": 1.3, "3 min": 1.6, "5 min": 2.0, "10 min": 3.0}
    mult = tf_multiplier.get(selected_tf, 1.0)
    
    if "GOLD" in st.session_state.selected_asset: step = 0.50 * mult
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

# Пазарни изчисления и прецизиране по предходна свещ
ema_fast = calculate_ema(st.session_state.price_history, fast_p)
ema_mid = calculate_ema(st.session_state.price_history, mid_p)
ema_slow = calculate_ema(st.session_state.price_history, slow_p)

prices_list = list(st.session_state.price_history)
prev_candle_close = prices_list[-1] if len(prices_list) >= 1 else 0
prev_candle_open = prices_list[-2] if len(prices_list) >= 2 else 0
is_prev_candle_bullish = prev_candle_close > prev_candle_open
is_prev_candle_bearish = prev_candle_close < prev_candle_open

decision_text = "ИЗЧАКВАНЕ НА СИГНАЛ ⏳"
decision_color = "gray"

if ema_fast and ema_mid and ema_slow:
    if (ema_fast > ema_mid > ema_slow) and is_prev_candle_bullish:
        decision_text = "КУПУВАЙ (CALL) 🟢"
        decision_color = "#2ebd85"
    elif (ema_fast < ema_mid < ema_slow) and is_prev_candle_bearish:
        decision_text = "ПРОДАВАЙ (PUT) 🔴"
        decision_color = "#df294a"
    else:
        decision_text = "⚠️ НЕ ТЪРКУВАЙ! (Пазарна консолидация / Филтриран шум)"
        decision_color = "#ffa500"

# --- ЛАЙВ ДАШБОРД ФРАГМЕНТ (БЕЗ ВЛОЖЕНИ СТРУКТУРНИ ГРЕШКИ) ---
@st.fragment(run_every=1.0)
def render_live_dashboard():
    # Горна линия
    c1, c2 = st.columns(2)
    current_datetime = datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
    c1.markdown(f"🤖 **Pocket Option Pro Terminal** | Актив: `{st.session_state.selected_asset}`")
    c2.markdown(f"<div style='text-align: right; color: #aaaaaa; font-family: monospace;'>🕒 {current_datetime}</div>", unsafe_allow_html=True)
    
    # Решение
    st.markdown(f"""
        <div style="background-color:#11141a; padding:12px; border-radius:6px; border-left: 8px solid {decision_color}; text-align:center; margin-bottom: 10px;">
            <h1 style="color:{decision_color}; margin:0; font-size:26px; font-weight:bold;">{decision_text}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Графика
    chart_df = pd.DataFrame({"Цена": list(st.session_state.price_history)[-35:]})
    st.line_chart(chart_df, height=120, use_container_width=True)
    
    # Контроли (Падащо меню и Таймер)
    col_menu, col_timer = st.columns(2)
    
    try:
        current_index = all_otc_assets.index(st.session_state.selected_asset)
    except ValueError:
        current_index = 0
        
    with col_menu:
        chosen_asset = st.selectbox("Избор на актив:", all_otc_assets, index=current_index, disabled=st.session_state.is_running, label_visibility="collapsed", key="asset_select_box")
        
    rem_sec = max(0, required_seconds - int(time.time() - st.session_state.last_tick_time))
    
    with col_timer:
        if st.session_state.is_running:
            mins, secs = rem_sec // 60, rem_sec % 60
            st.markdown(f"<div style='text-align: right; font-size: 15px; margin-top: 5px;'>⏱️ Вход след: <b>{mins:02d}:{secs:02d}</b></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: right; color: #888; margin-top: 5px;'>⏳ Ботът е спрян</div>", unsafe_allow_html=True)

    # Тригър за нова свещ
    if chosen_asset != st.session_state.selected_asset:
        st.session_state.selected_asset = chosen_asset
        st.session_state.price_history = generate_fresh_history(chosen_asset)
        st.session_state.current_price = st.session_state.price_history[-1]
        st.session_state.start_price = st.session_state.price_history[-1]
        st.st.rerun()
        
    if st.session_state.is_running and rem_sec == 0:
        st.rerun()

    st.write("")
    
    # Метричен ред (Подравнен изцяло линейно)
    m1, m2, m3 = st.columns(3)
    decimals = 2 if any(x in st.session_state.selected_asset for x in ["GOLD", "SILVER", "APPLE", "GOOGLE", "META", "NVIDIA", "NETFLIX", "TESLA", "MICROSOFT", "AMAZON", "TRY"]) else 5
    denom = st.session_state.start_price if st.session_state.start_price != 0 else 1.1234
    pct_change = ((st.session_state.current_price - st.session_state.start_price) / denom) * 100
    
