import streamlit as st
import time
import random
import pandas as pd

# Настройка на уеб страницата
st.set_page_config(
    page_title="Pocket Option 3 EMA Web Bot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стилове за тъмна тема и красиви панели
st.markdown("""
    <style>
    .main { background-color: #1c1f26; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# Списък с всички популярни OTC двойки в Pocket Option
otc_pairs = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "EUR/GBP (OTC)", "USD/CAD (OTC)", "NZD/USD (OTC)", "EUR/JPY (OTC)"
]

# --- ИНИЦИАЛИЗАЦИЯ НА СЕСИЙНИТЕ ПРОМЕНЛИВИ (SESSION STATE) ---
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = "EUR/USD (OTC)"

# Функция за генериране на нова пазарна история при смяна на актива
def generate_fresh_history(asset_name):
    base_price = 145.25 if "JPY" in asset_name else 1.1234
    history = []
    for _ in range(150):
        step = 0.02 if "JPY" in asset_name else 0.0003
        base_price += random.choice([-step, -step/2, step/2, step])
        history.append(round(base_price, 5))
    return history

if "price_history" not in st.session_state:
    st.session_state.price_history = generate_fresh_history(st.session_state.selected_asset)
if "current_price" not in st.session_state:
    st.session_state.current_price = st.session_state.price_history[-1]
if "start_price" not in st.session_state:
    st.session_state.start_price = st.session_state.price_history[-1]
if "logs" not in st.session_state:
    st.session_state.logs = []

# --- ФУНКЦИИ ЗА ИЗЧИСЛЕНИЕ ---
def calculate_ema(prices, period):
    if len(prices) < period:
        return None
    sma = sum(prices[:period]) / period
    multiplier = 2 / (period + 1)
    ema = sma
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    return round(ema, 5)

def add_log(msg):
    timestamp = time.strftime("[%H:%M:%S] ")
    st.session_state.logs.append(timestamp + msg)
    if len(st.session_state.logs) > 50:
        st.session_state.logs.pop(0)

# --- СТРАНИЧЕН ПАНЕЛ (НАСТРОЙКИ ЗА УПРАВЛЕНИЕ) ---
st.sidebar.title("⚙️ Настройки на Бота")

# 1. Времева рамка
timeframes = ["1 min", "3 min", "5 min"]
selected_tf = st.sidebar.selectbox("⏱️ Времева рамка:", timeframes, disabled=st.session_state.is_running)

# 2. Сума на сделка
stake = st.sidebar.number_input("💰 Сума на сделка ($):", min_value=1.0, max_value=1000.0, value=10.0, step=5.0, disabled=st.session_state.is_running)

# 3. Настройки за EMA индикаторите
st.sidebar.subheader("Индикатори (Периоди)")
fast_p = st.sidebar.number_input("Бърза EMA:", min_value=2, max_value=20, value=9, disabled=st.session_state.is_running)
mid_p = st.sidebar.number_input("Средна EMA:", min_value=10, max_value=50, value=21, disabled=st.session_state.is_running)
slow_p = st.sidebar.number_input("Бавна EMA:", min_value=20, max_value=200, value=50, disabled=st.session_state.is_running)

st.sidebar.markdown("---")

# Бутони за Старт и Стоп в страничната лента
if not st.session_state.is_running:
    if st.sidebar.button("🚀 СТАРТИРАЙ БОТ", use_container_width=True):
        if fast_p >= mid_p or mid_p >= slow_p:
            st.sidebar.error("Грешка: Подредбата трябва да е Бърза < Средна < Бавна!")
        else:
            st.session_state.is_running = True
            st.session_state.start_price = st.session_state.current_price
            add_log(f"СТАРТ: {st.session_state.selected_asset} | Рамка: {selected_tf} | Базова цена: {st.session_state.start_price}")
            st.rerun()
else:
    if st.sidebar.button("🛑 СПРИ БОТ", use_container_width=True):
        st.session_state.is_running = False
        add_log("СТОП: Ботът преустанови анализите.")
        st.rerun()


# --- ОСНОВЕН ПАНЕЛ (УЕБ ИНТЕРФЕЙС) ---
st.title("🤖 Pocket Option 3 EMA Web Bot Analytics")

# --- СЕКЦИЯ: ОТДЕЛНИ БУТОНИ ЗА ВСЯКА ТЪРГОВСКА ДВОЙКА ---
st.subheader("📈 Търговски активи (Pocket Option OTC)")

col_a, col_b, col_c, col_d = st.columns(4)
cols = [col_a, col_b, col_c, col_d]

for idx, asset in enumerate(otc_pairs):
    target_col = cols[idx % 4]
    with target_col:
        button_label = f"⭐ {asset}" if asset == st.session_state.selected_asset else asset
        if st.button(button_label, key=f"btn_{asset}", use_container_width=True, disabled=st.session_state.is_running):
            st.session_state.selected_asset = asset
            st.session_state.price_history = generate_fresh_history(asset)
            st.session_state.current_price = st.session_state.price_history[-1]
            st.session_state.start_price = st.session_state.price_history[-1]
            add_log(f"🔄 Превключване на актив: {asset}")
            st.rerun()

st.write("")

# --- МАТЕМАТИЧЕСКИ ИЗЧИСЛЕНИЯ И АНАЛИЗ ---
ema_fast = calculate_ema(st.session_state.price_history, fast_p)
ema_mid = calculate_ema(st.session_state.price_history, mid_p)
ema_slow = calculate_ema(st.session_state.price_history, slow_p)

decision_text = "ИЗЧАКВАНЕ НА СИГНАЛ ⏳"
decision_color = "gray"

if ema_fast and ema_mid and ema_slow:
    if ema_fast > ema_mid > ema_slow:
        decision_text = "КУПУВАЙ (CALL / HIGHER) 🟢 [ТЕНДЕНЦИЯ: НАГОРЕ]"
        decision_color = "#2ebd85"
        if st.session_state.is_running and (len(st.session_state.logs) == 0 or "CALL" not in st.session_state.logs[-1]):
            add_log(f"🟢 СИГНАЛ ЗА ПЕЧАЛБА: CALL на {st.session_state.selected_asset} при цена {st.session_state.current_price}")
    elif ema_fast < ema_mid < ema_slow:
        decision_text = "ПРОДАВАЙ (PUT / LOWER) 🔴 [ТЕНДЕНЦИЯ: НАДОЛУ]"
        decision_color = "#df294a"
        if st.session_state.is_running and (len(st.session_state.logs) == 0 or "PUT" not in st.session_state.logs[-1]):
            add_log(f"🔴 СИГНАЛ ЗА ПЕЧАЛБА: PUT на {st.session_state.selected_asset} при цена {st.session_state.current_price}")
    else:
        decision_text = "НЕ ТЪРГУВАЙ! ⚠️ (Странично движение / Флат)"
        decision_color = "#ffa500"

# Блок 1: Голям визуален прозорец за РЕШЕНИЕТО (Включва и текущата валутна двойка)
st.markdown(f"""
    <div style="background-color:#11141a; padding:25px; border-radius:10px; border-left: 10px solid {decision_color}; text-align:center;">
        <h2 style="color:#aaaaaa; margin:0; font-size:14px; letter-spacing: 1px;">ТЕКУЩ АКТИВ ЗА ТЪРГОВИЯ: <span style="color:#ffffff; font-weight:bold;">{st.session_state.selected_asset}</span></h2>
        <hr style="border: 0; border-top: 1px solid #2b303c; margin: 15px 0;">
        <h2 style="color:#aaaaaa; margin:0; font-size:16px; letter-spacing: 1px;">АКТИВЕН АНАЛИЗ ЗА ВХОД (РЕАЛНО ВРЕМЕ):</h2>
        <h1 style="color:{decision_color}; margin:15px 0 0 0; font-size:36px; font-weight:bold;">{decision_text}</h1>
    </div>
""", unsafe_allow_html=True)

st.write("")

# --- ⏱️ СЕКЦИЯ: ИЗЧИСТЕН ЦИФРОВ ТАЙМЕР ЗА ВРЕМЕВИ РАМКИ ⏱️ ---
timer_placeholder = st.empty()

# Блок 2: Метрики (Цена, Проценти, Индикатори)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label=f"Текуща Цена ({st.session_state.selected_asset.split()[0]})", value=f"{st.session_state.current_price:.5f}")

with col2:
    denom = st.session_state.start_price if st.session_state.start_price != 0 else 1.1234
    pct_change = ((st.session_state.current_price - st.session_state.start_price) / denom) * 100
    st.metric(label="Промяна на сесията", value=f"{pct_change:.3f}%", delta=f"{pct_change:.3f}%")

with col3:
    st.metric(label=f"EMA ({fast_p}/{mid_p}/{slow_p})", value=f"{ema_fast} | {ema_mid} | {ema_slow}")

# Блок 3: Интерактивна Трейдинг Графика
st.subheader("📊 Пазарна графика в реално време")
chart_data = pd.DataFrame({
    'Цена': list(st.session_state.price_history)[-60:],
})
st.line_chart(chart_data, height=250)

# Блок 4: Терминал / Журнал
st.subheader("📝 Терминал в реално време")
log_text = "\n".join(st.session_state.logs[::-1])
st.text_area(label="", value=log_text, height=150, disabled=True)

# --- АВТОМАТИЧНО ПРЕЗАРЕЖДАНЕ И СИНХРОНИЗИРАН ТАЙМЕР ---
if st.session_state.is_running:
    # Преобразуване на времевата рамка в реални секунди (1 мин = 60 сек, 3 мин = 180 сек, 5 мин = 300 сек)
    tf_to_seconds = {"1 min": 60, "3 min": 180, "5 min": 300}
    total_seconds = tf_to_seconds.get(selected_tf, 60)
    
    start_time = time.time()
    
    # Луп за обратно броене на всяка секунда
    while True:
        elapsed = time.time() - start_time
        remaining = total_seconds - int(elapsed)
        
        if remaining <= 0:
            break
            
        # Форматиране на времето в стил MM:SS (без излишни милисекунди или десетични запетаи)
        mins = remaining // 60
        secs = remaining % 60
        time_string = f"{mins:02d}:{secs:02d}"
        
        with timer_placeholder.container():
            st.markdown(f"⏱️ **Време до следващ анализ на свещта за {st.session_state.selected_asset}:** `{time_string}`")
            
        time.sleep(1.0)

    # След изтичане на пълното време на свещта - Симулиране на нов пазарен тик
    step = 0.03 if "JPY" in st.session_state.selected_asset else 0.0003
    change = random.choice([-step, -step/2, 0, step/2, step])
    st.session_state.current_price = round(st.session_state.current_price + change, 5)
    st.session_state.price_history.append(st.session_state.current_price)
    
    # Презареждане и активиране на новия анализ
    timer_placeholder.empty()
    st.rerun()
else:
    timer_placeholder.info("Ботът е спрян. Изберете актив и натиснете 'СТАРТИРАЙ БОТ', за да стартирате анализа на времевата рамка.")

    st.rerun()
