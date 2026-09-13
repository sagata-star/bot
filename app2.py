import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta

# 1. Настройка на уеб страницата
st.set_page_config(
    page_title="PO 3 EMA Bot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Инжектиране на базови CSS стилове за структурата (без HTML стрелки)
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. --- СПИСЪК С OTC АКТИВА НА POCKET OPTION ---
all_otc_assets = [
    "BHD/CNY (OTC)", "CHF/NOK (OTC)", "EUR/TRY (OTC)", "LBP/USD (OTC)", 
    "MAD/USD (OTC)", "OMR/CNY (OTC)", "USD/ARC (OTC)", "USD/COP (OTC)", 
    "USD/MYR (OTC)", "ZAR/USD (OTC)", "USD/PKR (OTC)", "GBP/JPY (OTC 2)",
    "BTC/USD (OTC)", "ETH/USD (OTC)", "LTC/USD (OTC)", "USDT/RUB (OTC)",
    "US Tech 100 (OTC)", "US SPX 500 (OTC)", "Germany 40 (OTC)", 
    "AUD/CHF (OTC)", "EUR/NZD (OTC)", "GBP/NZD (OTC)",
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "EUR/GBP (OTC)", "USD/CAD (OTC)", "NZD/USD (OTC)", "EUR/JPY (OTC)",
    "GBP/JPY (OTC)", "EUR/CAD (OTC)", "AUD/CAD (OTC)", "USD/CHF (OTC)",
    "EUR/CHF (OTC)", "CAD/JPY (OTC)", "AUD/JPY (OTC)", "CHF/JPY (OTC)",
    "GBP/CAD (OTC)", "EUR/AUD (OTC)", "AUD/NZD (OTC)",
    "CAD/CHF (OTC)", "GBP/AUD (OTC)", "GBP/CHF (OTC)",
    "NZD/CAD (OTC)", "NZD/CHF (OTC)", "NZD/JPY (OTC)",
    "USD/TRY (OTC)", "EUR/ZAR (OTC)", "USD/ZAR (OTC)", "USD/THB (OTC)", 
    "USD/SGD (OTC)", "USD/RUB (OTC)", "EUR/RUB (OTC)", "USD/PLN (OTC)", 
    "USD/NOK (OTC)", "USD/SEK (OTC)", "USD/MXN (OTC)", "USD/INR (OTC)",
    "USD/HKD (OTC)", "USD/DKK (OTC)", "USD/CNH (OTC)", "USD/BRL (OTC)",
    "USD/ARS (OTC)", "AED/CNY (OTC)", "NGN/USD (OTC)", "KES/USD (OTC)", 
    "UAH/USD (OTC)", "GOLD (OTC)", "SILVER (OTC)", "APPLE (OTC)", "GOOGLE (OTC)", 
    "MICROSOFT (OTC)", "AMAZON (OTC)", "TESLA (OTC)", "META (OTC)", 
    "NVIDIA (OTC)", "NETFLIX (OTC)",
    "EUR/AUD (OTC)", "GBP/CHF (OTC)", "AUD/NZD (OTC)", "CAD/CHF (OTC)",
    "EUR/CAD (OTC)", "GBP/CAD (OTC)", "NZD/USD (OTC)", "USD/SGD (OTC)",
    "USD/HKD (OTC)", "EUR/NZD (OTC)", "GBP/NZD (OTC)", "CHF/JPY (OTC)",
    "AUD/JPY (OTC)", "CAD/JPY (OTC)", "NZD/JPY (OTC)", "EUR/CHF (OTC)",
    "USD/MXN (OTC)", "GBP/AUD (OTC)", "AUD/CAD (OTC)", "USD/NOK (OTC)"
]

# 4. Функция за генериране на изкуствена история
def generate_fresh_history(asset_name, tf_seconds):
    if "JPY" in asset_name: base_price = 145.25
    elif "CHF" in asset_name and "JPY" not in asset_name: base_price = 0.8950
    elif "GOLD" in asset_name: base_price = 2350.00
    elif "SILVER" in asset_name: base_price = 28.50
    elif "BTC" in asset_name: base_price = 64500.00
    elif "ETH" in asset_name: base_price = 3450.00
    elif "US Tech" in asset_name or "SPX" in asset_name: base_price = 5400.00
    elif "COP" in asset_name: base_price = 4150.00
    elif "PKR" in asset_name: base_price = 278.00
    elif "LBP" in asset_name: base_price = 0.000011
    elif any(x in asset_name for x in ["APPLE", "GOOGLE", "META", "NVIDIA", "NETFLIX", "TESLA", "MICROSOFT", "AMAZON"]):
        base_price = random.uniform(150.00, 450.00)
    else: base_price = 1.1234

    prices = []
    times = []
    current_time = datetime.now() - timedelta(seconds=250 * tf_seconds)
    current_price = base_price
    
    for i in range(250):
        current_price += random.uniform(-base_price * 0.0005, base_price * 0.0005)
        prices.append(current_price)
        times.append(current_time + timedelta(seconds=i * tf_seconds))
        
    return pd.DataFrame({"Timestamp": times, "Price": prices})

# 5. НАСТРОЙКИ В СТРАНИЧНИЯ ПАНЕЛ
st.title("🤖 PO 3 EMA Bot Dashboard")

selected_asset = st.sidebar.selectbox("Избор на актив:", all_otc_assets, index=0)

timeframe_label = st.sidebar.selectbox(
    "Времеви диапазон (Таймфрейм):",
    options=["5 сек", "15 сек", "30 сек", "1 мин", "3 мин", "5 мин", "10 мин"],
    index=3
)

tf_mapping = {
    "5 сек": 5, "15 сек": 15, "30 сек": 30,
    "1 мин": 60, "3 мин": 180, "5 мин": 300, "10 мин": 600
}
tf_seconds = tf_mapping[timeframe_label]

# Адаптивни ЕМА периоди и прагове за волатилност
if tf_seconds < 60:
    p_fast, p_mid, p_slow = 12, 24, 50
    volatility_threshold = 0.025
else:
    p_fast, p_mid, p_slow = 8, 14, 21
    volatility_threshold = 0.012

st.sidebar.write("---")
st.sidebar.markdown(f"📊 **Динамични настройки:**")
st.sidebar.text(f"Бърза: EMA {p_fast}")
st.sidebar.text(f"Средна: EMA {p_mid}")
st.sidebar.text(f"Бавна: EMA {p_slow}")

# 6. СИНХРОНИЗАЦИЯ И СТАБИЛИЗАЦИЯ НА БАЗОВИТЕ ДАННИ
if "current_asset" not in st.session_state or st.session_state.current_asset != selected_asset or "current_tf" not in st.session_state or st.session_state.current_tf != tf_seconds:
    st.session_state.current_asset = selected_asset
    st.session_state.current_tf = tf_seconds
    st.session_state.df_history = generate_fresh_history(selected_asset, tf_seconds)
    st.session_state.last_update_timestamp = int(time.time() / tf_seconds)
    st.session_state.force_calculation = True

# Проверка дали времевата рамка е изтекла, за да генерираме нова свещ
current_timestamp_bucket = int(time.time() / tf_seconds)
if current_timestamp_bucket != st.session_state.last_update_timestamp:
    st.session_state.last_update_timestamp = current_timestamp_bucket
    last_price = st.session_state.df_history["Price"].iloc[-1]
    new_price = last_price + random.uniform(-last_price * 0.0005, last_price * 0.0005)
    new_row = pd.DataFrame({"Timestamp": [datetime.now()], "Price": [new_price]})
    st.session_state.df_history = pd.concat([st.session_state.df_history.iloc[1:], new_row], ignore_index=True)
    st.session_state.force_calculation = True

if "current_p" not in st.session_state:
    st.session_state.force_calculation = True

# 7. ТЕХНИЧЕСКИ АНАЛИЗ (Изпълнява се само при нова свещ)
if st.session_state.get("force_calculation", True):
    df_calc = st.session_state.df_history.copy()
    
    df_calc['EMA_Fast'] = df_calc['Price'].ewm(span=p_fast, adjust=False).mean()
    df_calc['EMA_Mid'] = df_calc['Price'].ewm(span=p_mid, adjust=False).mean()
    df_calc['EMA_Slow'] = df_calc['Price'].ewm(span=p_slow, adjust=False).mean()
    
    window_size = min(20, len(df_calc))
    df_calc['Volatility_SD'] = (df_calc['Price'].rolling(window=window_size).std() / df_calc['Price']) * 100
    df_calc['EMA_Fast_Slope'] = df_calc['EMA_Fast'].diff(1) / df_calc['EMA_Fast'].shift(1) * 100

    st.session_state.current_p = df_calc['Price'].iloc[-1]
    st.session_state.emaFast_p = df_calc['EMA_Fast'].iloc[-1]
    st.session_state.emaMid_p = df_calc['EMA_Mid'].iloc[-1]
    st.session_state.emaSlow_p = df_calc['EMA_Slow'].iloc[-1]
    st.session_state.emaFast_prev = df_calc['EMA_Fast'].iloc[-2]
    st.session_state.emaSlow_prev = df_calc['EMA_Slow'].iloc[-2]
    st.session_state.current_volatility = df_calc['Volatility_SD'].fillna(0.0).iloc[-1]
    st.session_state.fast_ema_slope = df_calc['EMA_Fast_Slope'].fillna(0.0).iloc[-1]
    
    st.session_state.force_calculation = False

current_p = st.session_state.current_p
emaFast_p = st.session_state.emaFast_p
emaMid_p = st.session_state.emaMid_p
emaSlow_p = st.session_state.emaSlow_p
emaFast_prev = st.session_state.emaFast_prev
emaSlow_prev = st.session_state.emaSlow_prev
current_volatility = st.session_state.current_volatility
fast_ema_slope = st.session_state.fast_ema_slope

ema_spread_pct = (abs(emaFast_p - emaSlow_p) / emaSlow_p) * 100 if emaSlow_p > 0 else 0.0

is_low_volatility = current_volatility < (volatility_threshold * 0.4) or ema_spread_pct < (volatility_threshold * 0.5)
is_intertwined = (emaFast_p > emaSlow_p and emaFast_prev < emaSlow_prev) or (emaFast_p < emaSlow_p and emaFast_prev > emaSlow_prev)
is_strong_momentum = abs(fast_ema_slope) > 0.002

if current_p < 0.01: fmt_str = "{:.6f}"
elif current_p < 1000: fmt_str = "{:.4f}"
else: fmt_str = "{:.2f}"

# --- ИЗОЛИРАН ФРАГМЕНТ САМО ЗА СЕКУНДНИЯ ТАЙМЕР ---
@st.fragment(run_every=1.0)
def render_live_timer(tf_seconds, timeframe_label):
    remaining_seconds = tf_seconds - (int(time.time()) % tf_seconds)
    if remaining_seconds == tf_seconds or remaining_seconds <= 0:
        st.rerun()
    st.metric(f"⏳ Край на текущата свещ ({timeframe_label})", f"{remaining_seconds} сек.")

st.write("---")
t_col1, t_col2 = st.columns(2)
with t_col1:
    render_live_timer(tf_seconds, timeframe_label)
with t_col2:
    st.metric(f"Цена на актив {selected_asset}", fmt_str.format(current_p))


# --- 8. СРЕДЕН ПАНЕЛ: ОФИЦИАЛНИ STREAMLIT ИКОНИ И СТРЕЛКИ ---
st.write("---")
st.subheader("🎯 Технически Анализ & Направление на тренда")

# Изчисляване на състоянието и задаване на официални текстови параметри
if is_low_volatility:
    buy_ratio = random.randint(49, 51)
    direction_title = "⚠️ СТАГНАЦИЯ / РЕЙНДЖ"
    direction_subtitle = "↔️ ПАЗАРЪТ Е СТАТИЧЕН"
    status_text = f"⚠️ НИСКА ВОЛАТИЛНОСТ: Пазарът няма сила на {timeframe_label}."
    alert_type = "warning"
elif is_intertwined:
    buy_ratio = random.randint(46, 54)
    direction_title = "❌ ФАЛШИВ ПРОБИВ"
    direction_subtitle = "🔄 ЛИНИИТЕ СЕ ПРЕПЛИТАТ"
    status_text = f"📉 ПРЕПЛИТАНЕ НА ЛИНИИТЕ: Странично движение (Флат) за {timeframe_label}."
    alert_type = "warning"
elif emaFast_p > emaMid_p > emaSlow_p:
    if current_p >= emaFast_p and is_strong_momentum and fast_ema_slope > 0:
        buy_ratio = random.randint(88, 98)
        direction_title = "🟢 [ STRONG BUY ]"
        direction_subtitle = "🚀 ПОСОКА: НАГОРЕ (УСКОРЕНИЕ)"
        status_text = f"🔥 СИЛЕН ТРЕНД: Ускоряващо движение нагоре (Бичи пазар) на {timeframe_label}."
        alert_type = "success"
    else:
        buy_ratio = random.randint(58, 68)
        direction_title = "🟡 [ WEAK BUY ]"
