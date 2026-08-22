import streamlit as st
import time
import random
import pandas as pd

# Настройка на уеб страницата
st.set_page_config(
    page_title="Pocket Option 3 EMA Web Bot",
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

# Инициализация на сесийни променливи (Session State), за да не се губят данните при опресняване
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "price_history" not in st.session_state:
    # Пълнене на първоначална история от цени
    base_price = 1.1234
    history = []
    for _ in range(100):
        base_price += random.choice([-0.0003, -0.0001, 0.0001, 0.0003])
        history.append(base_price)
    st.session_state.price_history = history
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

# --- СТРАНИЧЕН ПАНЕЛ (НАСТРОЙКИ) ---
st.sidebar.title("⚙️ Настройки на Бота")

# 1. Избор на Актив
otc_pairs = ["EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)", "EUR/GBP (OTC)", "USD/CAD (OTC)"]
selected_asset = st.sidebar.selectbox("📈 Валутна двойка:", otc_pairs, disabled=st.session_state.is_running)

# 2. Времева рамка
timeframes = ["1 min", "3 min", "5 min"]
selected_tf = st.sidebar.selectbox("⏱️ Времева рамка:", timeframes, disabled=st.session_state.is_running)

# 3. Сума
stake = st.sidebar.number_input("💰 Сума на сделка ($):", min_value=1.0, max_value=1000.0, value=10.0, step=5.0, disabled=st.session_state.is_running)

# 4. Настройки за EMA индикаторите
st.sidebar.subheader("Индикатори (Периоди)")
fast_p = st.sidebar.number_input("Бърза EMA:", min_value=2, max_value=20, value=9, disabled=st.session_state.is_running)
mid_p = st.sidebar.number_input("Средна EMA:", min_value=10, max_value=50, value=21, disabled=st.session_state.is_running)
slow_p = st.sidebar.number_input("Бавна EMA:", min_value=20, max_value=200, value=50, disabled=st.session_state.is_running)

# Бутони за Старт и Стоп
if not st.session_state.is_running:
    if st.sidebar.button("🚀 СТАРТИРАЙ БОТ", use_container_width=True):
        if fast_p >= mid_p or mid_p >= slow_p:
            st.sidebar.error("Грешка: Подредбата трябва да е Бърза < Средна < Бавна!")
        else:
            st.session_state.is_running = True
            st.session_state.start_price = st.session_state.current_price
            add_log(f"СТАРТ: {selected_asset} | Рамка: {selected_tf} | Базова цена: {st.session_state.start_price}")
            st.rerun()
else:
    if st.sidebar.button("🛑 СПРИ БОТ", use_container_width=True):
        st.session_state.is_running = False
        add_log("СТОП: Ботът преустанови анализите.")
        st.rerun()

# --- ОСНОВЕН ПАНЕЛ (УЕБ ИНТЕРФЕЙС) ---
st.title("🤖 Pocket Option 3 EMA Web Bot Analytics")

# Изчисляване на показатели
ema_fast = calculate_ema(st.session_state.price_history, fast_p)
ema_mid = calculate_ema(st.session_state.price_history, mid_p)
ema_slow = calculate_ema(st.session_state.price_history, slow_p)

# Решение и Пазарен Анализ
decision_text = "ИЗЧАКВАНЕ НА СИГНАЛ ⏳"
decision_color = "gray"

if ema_fast and ema_mid and ema_slow:
    if ema_fast > ema_mid > ema_slow:
        decision_text = "КУПУВАЙ (CALL / HIGHER) 🟢"
        decision_color = "green"
        if st.session_state.is_running and (len(st.session_state.logs) == 0 or "CALL" not in st.session_state.logs[-1]):
            add_log(f"🟢 СИГНАЛ: CALL на цена {st.session_state.current_price}")
    elif ema_fast < ema_mid < ema_slow:
        decision_text = "ПРОДАВАЙ (PUT / LOWER) 🔴"
        decision_color = "red"
        if st.session_state.is_running and (len(st.session_state.logs) == 0 or "PUT" not in st.session_state.logs[-1]):
            add_log(f"🔴 СИГНАЛ: PUT на цена {st.session_state.current_price}")
    else:
        decision_text = "НЕ ТЪРГУВАЙ! ⚠️ (Странично движение)"
        decision_color = "orange"

# Блок 1: Голям визуален прозорец за РЕШЕНИЕТО
st.markdown(f"""
    <div style="background-color:#11141a; padding:20px; border-radius:10px; border-left: 8px solid {decision_color}; text-align:center;">
        <h2 style="color:white; margin:0;">ПРЕПОРЪКА ЗА ТЪРГОВИЯ:</h2>
        <h1 style="color:{decision_color}; margin:10px 0 0 0; font-size:32px;">{decision_text}</h1>
    </div>
""", unsafe_allow_html=True)

st.write("")

# Блок 2: Метрики (Цена, Проценти, Индикатори)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Текуща Цена", value=f"{st.session_state.current_price:.5f}")

with col2:
    pct_change = ((st.session_state.current_price - st.session_state.start_price) / st.session_start_price) * 100
    st.metric(label="Промяна на сесията", value=f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")

with col3:
    st.metric(label=f"EMA ({fast_p}/{mid_p}/{slow_p})", value=f"{ema_fast} | {ema_mid} | {ema_slow}")

# Блок 3: Интерактивна Трейдинг Графика
st.subheader("📊 Пазарна графика в реално време")
chart_data = pd.DataFrame({
    'Цена': list(st.session_state.price_history)[-50:],
})
st.line_chart(chart_data, height=250)

# Блок 4: Терминал / Журнал
st.subheader("📝 Терминал в реално време")
log_text = "\n".join(st.session_state.logs[::-1])
st.text_area(label="", value=log_text, height=150, disabled=True)

# --- ЛУП ЗА АВТОМАТИЧНО ОПРЕШНЯВАНЕ (АКО БОТЪТ РАБОТИ) ---
if st.session_state.is_running:
    # Симулиране на следващ пазарен тик
    step = 0.0003 if st.session_state.current_price < 5 else 0.03
    change = random.choice([-step, -step/2, 0, step/2, step])
    st.session_state.current_price = round(st.session_state.current_price + change, 5)
    st.session_state.price_history.append(st.session_state.current_price)
    
    # Скорост на уеб опресняване спрямо фрейма
    intervals = {"1 min": 1.0, "3 min": 2.0, "5 min": 3.0}
    time.sleep(intervals.get(selected_tf, 1.0))
    st.rerun()
