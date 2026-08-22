import streamlit as st
import time
import random

# Настройка на уеб страницата
st.set_page_config(
    page_title="Pocket Option EMA+RSI Web Bot",
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

# --- ОПТИМИЗИРАНО КЕШИРАНЕ ЗА ПО-БЪРЗО ЗАРЕЖДАНЕ ---
@st.cache_data(ttl=600)
def generate_fresh_history(asset_name):
    base_price = 145.25 if "JPY" in asset_name else 1.1234
    history = []
    # 80 точки са напълно достатъчни за ЕМА 50 и RSI 14
    for _ in range(80):
        step = 0.02 if "JPY" in asset_name else 0.0003
        base_price += random.choice([-step, -step/2, step/2, step])
        history.append(round(base_price, 5))
    return history

# --- ИНИЦИАЛИЗАЦИЯ НА СЕСИЙНИТЕ ПРОМЕНЛИВИ ---
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = "EUR/USD (OTC)"
if "price_history" not in st.session_state:
    st.session_state.price_history = generate_fresh_history(st.session_state.selected_asset)
if "current_price" not in st.session_state:
    st.session_state.current_price = st.session_state.price_history[-1]
if "start_price" not in st.session_state:
    st.session_state.start_price = st.session_state.price_history[-1]
if "logs" not in st.session_state:
    st.session_state.logs = []

# --- МАТЕМАТИЧЕСКИ ФУНКЦИИ ЗА ИЗЧИСЛЕНИЕ ---
def calculate_ema(prices, period):
    if len(prices) < period:
        return None
    sma = sum(prices[:period]) / period
    multiplier = 2 / (period + 1)
    ema = sma
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    return round(ema, 5)

def calculate_rsi(prices, period=14):
    """ Изчислява Индекса на Относителната Сила (RSI) за по-висока точност """
    if len(prices) < period + 1:
        return 50.0  # Неутрална стойност по подразбиране
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
            
    # Вземане на последния прозорец от периода
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def add_log(msg):
    timestamp = time.strftime("[%H:%M:%S] ")
    st.session_state.logs.append(timestamp + msg)
    if len(st.session_state.logs) > 30:
        st.session_state.logs.pop(0)

# --- СТРАНИЧЕН ПАНЕЛ (НАСТРОЙКИ ЗА УПРАВЛЕНИЕ) ---
st.sidebar.title("⚙️ Конфигурация")

# Сума на сделка
stake = st.sidebar.number_input("💰 Сума на сделка ($):", min_value=1.0, max_value=1000.0, value=10.0, step=5.0, disabled=st.session_state.is_running)

# Настройки за ЕМА и RSI
st.sidebar.subheader("Индикатори за прецизност")
fast_p = st.sidebar.number_input("Бърза EMA:", min_value=2, max_value=20, value=9, disabled=st.session_state.is_running)
mid_p = st.sidebar.number_input("Средна EMA:", min_value=10, max_value=50, value=21, disabled=st.session_state.is_running)
slow_p = st.sidebar.number_input("Бавна EMA:", min_value=20, max_value=200, value=50, disabled=st.session_state.is_running)
rsi_p = st.sidebar.number_input("RSI Период:", min_value=5, max_value=30, value=14, disabled=st.session_state.is_running)

st.sidebar.markdown("---")

# Бутони за Старт и Стоп
if not st.session_state.is_running:
    if st.sidebar.button("🚀 СТАРТИРАЙ БОТ (1 МИН)", use_container_width=True):
        if fast_p >= mid_p or mid_p >= slow_p:
            st.sidebar.error("Грешка: Подредбата трябва да е Бърза < Средна < Бавна!")
        else:
            st.session_state.is_running = True
            st.session_state.start_price = st.session_state.current_price
            add_log(f"СТАРТ: {st.session_state.selected_asset} | Интервал: 1 min | Базова цена: {st.session_state.start_price}")
            st.rerun()
else:
    if st.sidebar.button("🛑 СПРИ БОТ", use_container_width=True):
        st.session_state.is_running = False
        add_log("СТОП: Ботът преустанови анализите.")
        st.rerun()

# --- ОСНОВЕН ПАНЕЛ (УЕБ ИНТЕРФЕЙС) ---
st.title("🤖 Pocket Option Pro: 3 EMA + RSI 1 min Analytics")

# --- СЕКЦИЯ: БУТОНИ ЗА ВАЛУТНИ ДВОЙКИ ---
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

# --- МАТЕМАТИЧЕСКИ ИЗЧИСЛЕНИЯ (EMA + RSI) ---
ema_fast = calculate_ema(st.session_state.price_history, fast_p)
ema_mid = calculate_ema(st.session_state.price_history, mid_p)
ema_slow = calculate_ema(st.session_state.price_history, slow_p)
current_rsi = calculate_rsi(st.session_state.price_history, rsi_p)

decision_text = "ИЗЧАКВАНЕ НА СИГНАЛ ⏳"
decision_color = "gray"

# Комбинирана логика за сигурен филтриран сигнал
if ema_fast and ema_mid and ema_slow:
    # Условие за Покупка (Възходящ тренд И пазарът НЕ Е прекупен)
    if (ema_fast > ema_mid > ema_slow) and (current_rsi < 70):
        decision_text = "КУПУВАЙ (CALL / HIGHER) 🟢"
        decision_color = "#2ebd85"
        if st.session_state.is_running and (len(st.session_state.logs) == 0 or "CALL" not in st.session_state.logs[-1]):
            add_log(f"🟢 СИГНАЛ (EMA+RSI): CALL на {st.session_state.selected_asset} | Цена: {st.session_state.current_price} | RSI: {current_rsi}")
            
    # Условие за Продажба (Низходящ тренд И пазарът НЕ Е препродаден)
    elif (ema_fast < ema_mid < ema_slow) and (current_rsi > 30):
        decision_text = "ПРОДАВАЙ (PUT / LOWER) 🔴"
        decision_color = "#df294a"
        if st.session_state.is_running and (len(st.session_state.logs) == 0 or "PUT" not in st.session_state.logs[-1]):
            add_log(f"🔴 СИГНАЛ (EMA+RSI): PUT на {st.session_state.selected_asset} | Цена: {st.session_state.current_price} | RSI: {current_rsi}")
            
    else:
        decision_text = "НЕ ТЪРГУВАЙ! ⚠️ (Линиите са оплетени или RSI е в екстремна зона)"
        decision_color = "#ffa500"

# Блок 1: Визуален прозорец за РЕШЕНИЕТО (С активна валутна двойка)
st.markdown(f"""
    <div style="background-color:#11141a; padding:25px; border-radius:10px; border-left: 10px solid {decision_color}; text-align:center;">
        <h2 style="color:#aaaaaa; margin:0; font-size:14px; letter-spacing: 1px;">АКТИВЕН ИНСТРУМЕНТ: <span style="color:#ffffff; font-weight:bold;">{st.session_state.selected_asset}</span></h2>
        <hr style="border: 0; border-top: 1px solid #2b303c; margin: 15px 0;">
        <h2 style="color:#aaaaaa; margin:0; font-size:16px; letter-spacing: 1px;">ПРЕЦИЗЕН АНАЛИЗ ЗА ВХОД (ОПРЕШНЯВАНЕ: 1 МИН):</h2>
        <h1 style="color:{decision_color}; margin:15px 0 0 0; font-size:36px; font-weight:bold;">{decision_text}</h1>
    </div>
""", unsafe_allow_html=True)

st.write("")

# --- ⏱️ СЕКЦИЯ: ИЗЧИСТЕН ЦИФРОВ ТАЙМЕР (БЕЗ СЕКУНДНИ ДЕКЛАРУМАЦИИ И ЛЕНТИ) ⏱️ ---
timer_placeholder = st.empty()

# Блок 2: Метрики
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label=f"Текуща Цена ({st.session_state.selected_asset.split()[0]})", value=f"{st.session_state.current_price:.5f}")

with col2:
    denom = st.session_state.start_price if st.session_state.start_price != 0 else 1.1234
    pct_change = ((st.session_state.current_price - st.session_state.start_price) / denom) * 100
    st.metric(label="Промяна на сесията", value=f"{pct_change:.3f}%", delta=f"{pct_change:.3f}%")

with col3:
    st.metric(label=f"EMA ({fast_p}/{mid_p}/{slow_p})", value=f"{ema_fast} | {ema_mid} | {ema_slow}")

with col4:
    # Защитно оцветяване на метриката за RSI според зоните
    rsi_delta = "Прекупеност ⚠️" if current_rsi >= 70 else ("Препродаденост ⚠️" if current_rsi <= 30 else "Стабилен пазар ✅")
    st.metric(label=f"RSI ({rsi_p}) Индикатор", value=f"{current_rsi}", delta=rsi_delta, delta_color="normal" if "Стабилен" in rsi_delta else "inverse")

# Блок 3: Терминал / Журнал
st.subheader("📝 Терминал за сигнали (Журнал)")
log_text = "\n".join(st.session_state.logs[::-1])
st.text_area(label="", value=log_text, height=150, disabled=True)

# --- АВТОМАТИЧНО ПРЕЗАРЕЖДАНЕ НА ВСЕКИ 1 МИНУТА (60 СЕКУНДИ) ---
if st.session_state.is_running:
    total_seconds = 60  # Твърдо фиксиран 1-минутен таймфрейм
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        remaining = total_seconds - int(elapsed)
        
        if remaining <= 0:
            break
            
        mins = remaining // 60
        secs = remaining % 60
        time_string = f"{mins:02d}:{secs:02d}"
        
