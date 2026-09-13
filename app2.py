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

# 2. Инжектиране на глобални CSS стилове
st.markdown("""
    <style>
    .main { background-color: #1c1f26; }
    div[data-testid="stMetricValue"] { font-size: 20px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 12px !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    h1 { font-size: 24px !important; margin-bottom: 5px !important; }
    h5 { font-size: 14px !important; margin-top: 5px !important; margin-bottom: 5px !important; }
    
    /* Стил за голямата цветна стрелка и текст */
    .direction-arrow { font-size: 70px !important; font-weight: bold; text-align: center; line-height: 1; }
    .direction-text { font-size: 28px !important; font-weight: bold; text-align: center; }
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
    # --- НОВИ 20 ВАЛУТНИ АКТИВА ---
    "EUR/AUD (OTC)", "GBP/CHF (OTC)", "AUD/NZD (OTC)", "CAD/CHF (OTC)",
    "EUR/CAD (OTC)", "GBP/CAD (OTC)", "NZD/USD (OTC)", "USD/SGD (OTC)",
    "USD/HKD (OTC)", "EUR/NZD (OTC)", "GBP/NZD (OTC)", "CHF/JPY (OTC)",
    "AUD/JPY (OTC)", "CAD/JPY (OTC)", "NZD/JPY (OTC)", "EUR/CHF (OTC)",
    "USD/MXN (OTC)", "GBP/AUD (OTC)", "AUD/CAD (OTC)", "USD/NOK (OTC)"
]

# 4. Funktion за генериране на базова история
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
    "1 мин": 60, "3 mint": 180, "5 мин": 300, "10 мин": 600
}
tf_mapping["3 мин"] = 180 
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

# Логика при настъпване на нова свещ
current_timestamp_bucket = int(time.time() / tf_seconds)
if current_timestamp_bucket != st.session_state.last_update_timestamp:
    st.session_state.last_update_timestamp = current_timestamp_bucket
    last_price = st.session_state.df_history["Price"].iloc[-1]
    new_price = last_price + random.uniform(-last_price * 0.0005, last_price * 0.0005)
    new_row = pd.DataFrame({"Timestamp": [datetime.now()], "Price": [new_price]})
    st.session_state.df_history = pd.concat([st.session_state.df_history.iloc[1:], new_row], ignore_index=True)


# --- 7. ЖИВО ТАБЛО И ИЗЧИСЛЕНИЯ НА ИНДИКАТОРИТЕ В РЕАЛНО ВРЕМЕ ---
@st.fragment(run_every=1.0)
def render_live_dashboard(timeframe_label, tf_seconds, selected_asset, p_fast, p_mid, p_slow, volatility_threshold):
    remaining_seconds = tf_seconds - (int(time.time()) % tf_seconds)
    
    # Ако таймерът изтече, рестартираме за генериране на нова свещ
    if remaining_seconds == tf_seconds or remaining_seconds <= 0:
        st.rerun()
        
    # Вземане на текущата история от сесията
    df_live = st.session_state.df_history.copy()

    # ДИНАМИЧНО ИЗЧИСЛЕНИЕ НА ТЕХНИЧЕСКИЯ АНАЛИЗ ЗА ТЕКУЩИЯ ТАЙМФРЕЙМ
    df_live['EMA_Fast'] = df_live['Price'].ewm(span=p_fast, adjust=False).mean()
    df_live['EMA_Mid'] = df_live['Price'].ewm(span=p_mid, adjust=False).mean()
    df_live['EMA_Slow'] = df_live['Price'].ewm(span=p_slow, adjust=False).mean()

    # Волатилност (Стандартно отклонение за последните 20 периода в %)
    df_live['Volatility_SD'] = (df_live['Price'].rolling(window=20).std() / df_live['Price']) * 100

    # Наклон/импулса (Slope) на бързата ЕМА
    df_live['EMA_Fast_Slope'] = df_live['EMA_Fast'].diff(1) / df_live['EMA_Fast'].shift(1) * 100

    # Текущи и предходни стойности
    current_p = df_live['Price'].iloc[-1]
    emaFast_p = df_live['EMA_Fast'].iloc[-1]
    emaMid_p = df_live['EMA_Mid'].iloc[-1]
    emaSlow_p = df_live['EMA_Slow'].iloc[-1]

    emaFast_prev = df_live['EMA_Fast'].iloc[-2]
    emaSlow_prev = df_live['EMA_Slow'].iloc[-2]

    current_volatility = df_live['Volatility_SD'].iloc[-1]
    fast_ema_slope = df_live['EMA_Fast_Slope'].iloc[-1]

    # Спред в проценти
    ema_spread_pct = (abs(emaFast_p - emaSlow_p) / emaSlow_p) * 100

    # Филтри за сигурност спрямо параметрите на избрания таймфрейм
    is_low_volatility = current_volatility < (volatility_threshold * 0.4) or ema_spread_pct < (volatility_threshold * 0.5)
    is_intertwined = (emaFast_p > emaSlow_p and emaFast_prev < emaSlow_prev) or (emaFast_p < emaSlow_p and emaFast_prev > emaSlow_prev)
    is_strong_momentum = abs(fast_ema_slope) > 0.005

    # Форматиране на цената на база актив
    if current_p < 0.01: fmt_str = "{:.6f}"
    elif current_p < 1000: fmt_str = "{:.4f}"
    else: fmt_str = "{:.2f}"

    # Визуализиране на горните метрики (Таймер и Цена)
    t_col1, t_col2 = st.columns(2)
    t_col1.metric(f"⏳ Опресняване след ({timeframe_label})", f"{remaining_seconds} сек.")
    t_col2.metric(f"Цена {selected_asset}", fmt_str.format(current_p))
    
    st.write("---")
    
    # СТРОГА ЛОГИКА ЗА СИГНАЛИТЕ И СТРЕЛКИТЕ
    if is_low_volatility:
        buy_ratio = random.randint(49, 51)
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠➡</div><div class='direction-text' style='color: #ffaa00;'>LOW VOLATILITY</div>"
        status_text = f"⚠️ НИСКА ВОЛАТИЛНОСТ: Пазарът няма сила на {timeframe_label}. Изчакайте разширение на диапазона."
        alert_type = "warning"
    elif is_intertwined:
        buy_ratio = random.randint(46, 54)
        arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡❌</div><div class='direction-text' style='color: #aaaaaa;'>FALSE BREAKOUT / CHOPPY</div>"
        status_text = f"📉 ПРЕПЛИТАНЕ НА ЛИНИИТЕ: Липса на посока и риск от фалшиви пробиви за {timeframe_label}."
        alert_type = "warning"
    elif emaFast_p > emaMid_p > emaSlow_p:
        if current_p >= emaFast_p and is_strong_momentum and fast_ema_slope > 0:
            buy_ratio = random.randint(88, 98)
            arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆🔥</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
