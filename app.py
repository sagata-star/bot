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
    initial_sidebar_state="collapsed"
)

# Агресивен CSS за премахване на абсолютно всички празни пространства и скролбарове
st.markdown("""
    <style>
    .main { background-color: #1c1f26; }
    div[data-testid="stMetricValue"] { font-size: 16px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 11px !important; margin-bottom: 0px !important; }
    div[data-testid="stMetric"] { padding: 2px !important; }
    .block-container { padding-top: 0.25rem !important; padding-bottom: 0.25rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    h1 { font-size: 18px !important; margin: 0px !important; padding: 0px !important; }
    h5 { font-size: 11px !important; margin: 1px 0px !important; }
    .stSelectbox, .stButton, .stNumberInput { margin-bottom: 0px !important; }
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

# --- ГОРНА ЛЕНТА: СТАТУС И ВРЕМЕ ---
top_left, top_right = st.columns(2)
current_datetime = datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
top_left.markdown(f"🤖 **Pocket Option Pro Terminal** | Активен: `{st.session_state.selected_asset}`")
top_right.markdown(f"<div style='text-align: right; color: #aaaaaa; font-family: monospace;'>🕒 {current_datetime}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top:2px; margin-bottom:5px; border-color:#333;'>", unsafe_allow_html=True)

# Изчисляване на пазарното време
timeframes = ["1 min", "2 min", "3 min", "5 min", "10 min"]
# За целите на пестене на място, дефинираме стойностите по подразбиране директно
selected_tf = "1 min" 

tf_to_seconds = {"1 min": 60, "2 min": 120, "3 min": 180, "5 min": 300, "10 min": 600}
required_seconds = tf_to_seconds.get(selected_tf, 60)
elapsed_seconds = int(time.time() - st.session_state.last_tick_time)
remaining_seconds = max(0, required_seconds - elapsed_seconds)

# Нов пазарен тик
if st.session_state.is_running and remaining_seconds == 0:
    step = 0.50 if "GOLD" in st.session_state.selected_asset else (0.02 if "JPY" in st.session_state.selected_asset else 0.0003)
    change = random.choice([-step, -step/2, 0, step/2, step])
    st.session_state.current_price = round(st.session_state.current_price + change, 5)
    st.session_state.price_history.append(st.session_price)
    if len(st.session_state.price_history) > 120:
        st.session_state.price_history.pop(0)
    st.session_state.last_tick_time = time.time()
    remaining_seconds = required_seconds

# Пазарни изчисления и прецизиране по предходна свещ
ema_fast = calculate_ema(st.session_state.price_history, 12)
ema_mid = calculate_ema(st.session_state.price_history, 26)
ema_slow = calculate_ema(st.session_state.price_history, 100)

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
        decision_text = "⚠️ НЕ ТЪРКУВАЙ!"
        decision_color = "#ffa500"

# --- ОСНОВНО РАЗДЕЛЕНИЕ В ДВЕ КОЛОНИ (СПЕСТЯВА 50% ВЕРТИКАЛНО МЯСТО) ---
main_left, main_right = st.columns([2, 3])

# --- ЛЯВА КОЛОНА: КОНФИГУРАЦИЯ, БУТОНИ И МЕТРИКИ ---
try:
    current_index = all_otc_assets.index(st.session_state.selected_asset)
except ValueError:
    current_index = 0

chosen_asset = main_left.selectbox("Избор на актив:", all_otc_assets, index=current_index, disabled=st.session_state.is_running, label_visibility="collapsed")

# Промяна на актива
if chosen_asset != st.session_state.selected_asset:
    st.session_state.selected_asset = chosen_asset
    st.session_state.price_history = generate_fresh_history(chosen_asset)
    st.session_state.current_price = st.session_state.price_history[-1]
    st.session_state.start_price = st.session_state.price_history[-1]
    st.rerun()

# Бутони за управление (Старт/Стоп) под менюто
ctrl_btn1, ctrl_btn2 = main_left.columns(2)
if not st.session_state.is_running:
    if ctrl_btn1.button("🚀 СТАРТ", use_container_width=True):
        st.session_state.is_running = True
        st.session_state.start_price = st.session_state.current_price
        st.session_state.last_tick_time = time.time()
        st.rerun()
else:
    if ctrl_btn2.button("🛑 СТОП", use_container_width=True):
        st.session_state.is_running = False
        st.rerun()

# Финансови метрики (Подредени компактно една под друга в лявата колона)
decimals = 2 if any(x in st.session_state.selected_asset for x in ["GOLD", "SILVER", "APPLE", "GOOGLE", "META", "NVIDIA", "NETFLIX", "TESLA", "MICROSOFT", "AMAZON", "TRY"]) else 5
denom = st.session_state.start_price if st.session_state.start_price != 0 else 1.1234
pct_change = ((st.session_state.current_price - st.session_state.start_price) / denom) * 100

main_left.metric(label="Текуща Цена", value=f"{st.session_state.current_price:.{decimals}f}")
main_left.metric(label="Промяна сесия", value=f"{pct_change:.3f}%", delta=f"{pct_change:.3f}%")
main_left.metric(label="Индикатори EMA", value=f"{ema_fast} | {ema_mid} | {ema_slow}")


# --- ДЯСНА КОЛОНА: РЕШЕНИЕ, ГРАФИКА И ТАЙМЕР ---
main_right.markdown(f"""
    <div style="background-color:#11141a; padding:6px; border-radius:4px; border-left: 6px solid {decision_color}; text-align:center; margin-bottom: 4px;">
        <h1 style="color:{decision_color}; margin:0; font-size:18px; font-weight:bold;">{decision_text}</h1>
    </div>
""", unsafe_allow_html=True)

# Графика
chart_df = pd.DataFrame({"Цена": list(st.session_state.price_history)[-30:]})
main_right.line_chart(chart_df, height=100, use_container_width=True)

# Таймер за вход под графиката вдясно
if st.session_state.is_running:
    mins, secs = remaining_seconds // 60, remaining_seconds % 60
    main_right.markdown(f"<div style='text-align: center; font-size: 13px; color: #aaaaaa;'>⏱️ Време до следващ вход: <b>{mins:02d}:{secs:02d}</b></div>", unsafe_allow_html=True)
else:
    main_right.markdown("<div style='text-align: center; font-size: 13px; color: #888;'>⏳ Ботът е спрян</div>", unsafe_allow_html=True)


# --- АВТОМАТИЧНО УЕБ ОПРЕСНЯВАНЕ НА ВСЯКА 1 СЕКУНДА ---
if st.session_state.is_running:
    st.markdown("""<meta http-equiv="refresh" content="1">""", unsafe_allow_html=True)
