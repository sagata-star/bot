import streamlit as st
import time
import random

# 1. Настройка на уеб страницата
st.set_page_config(
    page_title="Pocket Option 3 EMA Web Bot Ultra",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инжектиране на чисто CSS кодиране за стила на бутоните
st.markdown("""
    <style>
    .main { background-color: #1c1f26; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; }
    
    /* Активен зелен бутон */
    div.stButton > button[kind="primary"] {
        background-color: #2ebd85 !important;
        color: white !important;
        border: none !important;
        padding: 4px 6px !important;
        font-size: 11px !important;
        font-weight: bold !important;
    }
    
    /* Тъмни малки бутони */
    div.stButton > button[kind="secondary"] {
        background-color: #2b303c !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
        padding: 4px 6px !important;
        font-size: 11px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- СПИСЪЦИ С АКТИВИ ---
forex_pairs = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "EUR/GBP (OTC)", "USD/CAD (OTC)", "NZD/USD (OTC)", "EUR/JPY (OTC)",
    "GBP/JPY (OTC)", "EUR/CAD (OTC)", "AUD/CAD (OTC)", "USD/CHF (OTC)",
    "EUR/CHF (OTC)", "CAD/JPY (OTC)", "AUD/JPY (OTC)", "CHF/JPY (OTC)",
    "GBP/CAD (OTC)", "EUR/AUD (OTC)"
]
crypto_commodities = ["GOLD (OTC)", "SILVER (OTC)"]
stocks = [
    "APPLE (OTC)", "GOOGLE (OTC)", "MICROSOFT (OTC)", "AMAZON (OTC)", 
    "TESLA (OTC)", "META (OTC)", "NVIDIA (OTC)", "NETFLIX (OTC)"
]

# --- КЕШИРАНЕ НА ДАННИТЕ ---
@st.cache_data(ttl=600)
def generate_fresh_history(asset_name):
    if "JPY" in asset_name: base_price = 145.25
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
        else: step = 0.0003
        base_price += random.choice([-step, -step/2, step/2, step])
        history.append(round(base_price, 5))
    return history

# --- БЕЗОПАСНА ИНИЦИАЛИЗАЦИЯ НА СЕСИЯТА ---
if "is_running" not in st.session_state: st.session_state.is_running = False
if "selected_asset" not in st.session_state: st.session_state.selected_asset = "EUR/USD (OTC)"
if "price_history" not in st.session_state: st.session_state.price_history = generate_fresh_history(st.session_state.selected_asset)
if "current_price" not in st.session_state: st.session_state.current_price = st.session_state.price_history[-1]
if "start_price" not in st.session_state: st.session_state.start_price = st.session_state.price_history[-1]
if "logs" not in st.session_state: st.session_state.logs = []
if "last_tick_time" not in st.session_state: st.session_state.last_tick_time = time.time()

# --- МАТЕМАТИКА ---
def calculate_ema(prices, period):
    if len(prices) < period: return None
    sma = sum(prices[:period]) / period
    multiplier = 2 / (period + 1)
    ema = sma
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    return round(ema, 5)

def add_log(msg):
    timestamp = time.strftime("[%H:%M:%S] ")
    st.session_state.logs.append(timestamp + msg)
    if len(st.session_state.logs) > 25: st.session_state.logs.pop(0)

# --- СТРАНИЧЕН ПАНЕЛ ---
st.sidebar.title("⚙ Конфигурация")
timeframes = ["1 min", "2 min", "3 min", "5 min", "10 min"]
selected_tf = st.sidebar.selectbox("⏱ Времева рамка за анализ:", timeframes, disabled=st.session_state.is_running)
stake = st.sidebar.number_input("💰 Сума на сделка ($):", min_value=1.0, max_value=1000.0, value=10.0, step=5.0, disabled=st.session_state.is_running)

# Адаптивни периоди
if selected_tf == "1 min": default_fast, default_mid, default_slow = 12, 26, 100
elif selected_tf == "2 min": default_fast, default_mid, default_slow = 9, 21, 50
elif selected_tf == "3 min": default_fast, default_mid, default_slow = 7, 14, 30
else: default_fast, default_mid, default_slow = 5, 13, 34

fast_p = st.sidebar.number_input("Бърза EMA:", min_value=2, max_value=50, value=default_fast, disabled=st.session_state.is_running)
mid_p = st.sidebar.number_input("Средна EMA:", min_value=5, max_value=100, value=default_mid, disabled=st.session_state.is_running)
slow_p = st.sidebar.number_input("Бавна EMA:", min_value=10, max_value=200, value=default_slow, disabled=st.session_state.is_running)

# Управление на бутоните Старт/Стоп
if not st.session_state.is_running:
    if st.sidebar.button("🚀 СТАРТИРАЙ БОТ", use_container_width=True):
        st.session_state.is_running = True
        st.session_state.start_price = st.session_state.current_price
        st.session_state.last_tick_time = time.time()
        add_log(f"СТАРТ: {st.session_state.selected_asset} | Рамка: {selected_tf}")
        st.rerun()
else:
    if st.sidebar.button("🛑 СПРИ БОТ", use_container_width=True):
        st.session_state.is_running = False
        st.rerun()

# --- АВТОМАТИЧНО ИЗЧИСЛЕНИЕ НА ТИКА ПРИ ПРЕЗАРЕЖДАНЕ ---
tf_to_seconds = {"1 min": 60, "2 min": 120, "3 min": 180, "5 min": 300, "10 min": 600}
required_seconds = tf_to_seconds.get(selected_tf, 60)
current_time = time.time()

# Изчисляваме оставащото време
elapsed_seconds = int(current_time - st.session_state.last_tick_time)
remaining_seconds = max(0, required_seconds - elapsed_seconds)

# Ако времето е изтекло и ботът работи - генерираме нов тик БЕЗ уайл цикли
if st.session_state.is_running and remaining_seconds == 0:
    tf_multiplier = {"1 min": 1.0, "2 min": 1.3, "3 min": 1.6, "5 min": 2.0, "10 min": 3.0}
    mult = tf_multiplier.get(selected_tf, 1.0)
    
    if "GOLD" in st.session_state.selected_asset: step = 0.50 * mult
    elif "SILVER" in st.session_state.selected_asset: step = 0.05 * mult
    elif any(x in st.session_state.selected_asset for x in ["APPLE", "GOOGLE", "META", "NVIDIA", "NETFLIX", "TESLA", "MICROSOFT", "AMAZON"]): step = 0.12 * mult
    elif "JPY" in st.session_state.selected_asset: step = 0.02 * mult
    else: step = 0.0003 * mult
        
    change = random.choice([-step, -step/2, 0, step/2, step])
    st.session_state.current_price = round(st.session_state.current_price + change, 5)
    st.session_state.price_history.append(st.session_state.current_price)
    st.session_state.last_tick_time = time.time()
    remaining_seconds = required_seconds

# --- ОСНОВЕН ПАНЕЛ ---
st.title("🤖 Pocket Option Pro: Multi-Asset Terminal")
st.write("### 📈 Избор на търговски актив (Pocket Option OTC)")

def render_asset_grid(asset_list, num_columns=6):
    cols = st.columns(num_columns)
    for idx, asset in enumerate(asset_list):
        target_col = cols[idx % num_columns]
        with target_col:
            is_active = asset == st.session_state.selected_asset
            btn_type = "primary" if is_active else "secondary"
            if st.button(asset, key=f"btn_{asset}", type=btn_type, use_container_width=True, disabled=st.session_state.is_running):
                st.session_state.selected_asset = asset
                st.session_state.price_history = generate_fresh_history(asset)
                st.session_state.current_price = st.session_state.price_history[-1]
                st.session_state.start_price = st.session_state.price_history[-1]
                st.rerun()

st.write("##### 💱 Валутни двойки (Forex OTC)")
render_asset_grid(forex_pairs, num_columns=6)
st.write("##### 🏭 Стоки & 🏛 Световни Корпорации (Stocks OTC)")
render_asset_grid(crypto_commodities + stocks, num_columns=5)

# Математически сигнали
ema_fast = calculate_ema(st.session_state.price_history, fast_p)
ema_mid = calculate_ema(st.session_state.price_history, mid_p)
ema_slow = calculate_ema(st.session_state.price_history, slow_p)

decision_text = "ИЗЧАКВАНЕ НА СИГНАЛ ⏳"
decision_color = "gray"

if ema_fast and ema_mid and ema_slow:
    if ema_fast > ema_mid > ema_slow:
        decision_text = "КУПУВАЙ (CALL / HIGHER) 🟢"
        decision_color = "#2ebd85"
        if st.session_state.is_running and (len(st.session_state.logs) == 0 or "CALL" not in st.session_state.logs[-1]):
            add_log(f"🟢 СИГНАЛ: CALL на {st.session_state.selected_asset} при цена {st.session_state.current_price}")
    elif ema_fast < ema_mid < ema_slow:
        decision_text = "ПРОДАВАЙ (PUT / LOWER) 🔴"
        decision_color = "#df294a"
        if st.session_state.is_running and (len(st.session_state.logs) == 0 or "PUT" not in st.session_state.logs[-1]):
            add_log(f"🔴 СИГНАЛ: PUT на {st.session_state.selected_asset} при цена {st.session_state.current_price}")
    else:
        decision_text = "НЕ ТЪРКУВАЙ! ⚠️ (Пазарна консолидация / Флат)"
        decision_color = "#ffa500"

st.write("")
st.markdown(f"""
    <div style="background-color:#11141a; padding:25px; border-radius:10px; border-left: 10px solid {decision_color}; text-align:center;">
        <h2 style="color:#aaaaaa; margin:0; font-size:14px;">ТЕКУЩ АКТИВ: <span style="color:#ffffff; font-weight:bold;">{st.session_state.selected_asset}</span></h2>
        <hr style="border: 0; border-top: 1px solid #2b303c; margin: 15px 0;">
        <h1 style="color:{decision_color}; margin:0; font-size:32px; font-weight:bold;">{decision_text}</h1>
    </div>
""", unsafe_allow_html=True)

st.write("")

# Показване на таймера
if st.session_state.is_running:
    mins = remaining_seconds // 60
    secs = remaining_seconds % 60
    st.markdown(f"⏱️ **Време до следващ пазарен анализ:** `{mins:02d}:{secs:02d}`")
else:
    st.info("Ботът е спрян. Натиснете 'СТАРТИРАЙ БОТ' от страничната лента.")

# Метрики
