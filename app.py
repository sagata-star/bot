import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta

# =====================================================================
# 1. СТРАНИЧНА НАСТРОЙКА И СТИЛОВЕ
# =====================================================================
st.set_page_config(
    page_title="PO 3 EMA Bot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #1c1f26; }
    div[data-testid="stMetricValue"] { font-size: 20px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 12px !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    h1 { font-size: 24px !important; margin-bottom: 5px !important; }
    h5 { font-size: 14px !important; margin-top: 5px !important; margin-bottom: 5px !important; }
    .direction-arrow { font-size: 70px !important; font-weight: bold; text-align: center; line-height: 1; }
    .direction-text { font-size: 28px !important; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. ПЪЛЕН ОРИГИНАЛЕН СПИСЪК С НАД 80 OTC АКТИВА НА POCKET OPTION
# =====================================================================
all_otc_assets = [
    # Новите валутни двойки поискани от потребителя
    "BHD/CNY (OTC)", "CHF/NOK (OTC)", "EUR/TRY (OTC)", "LBP/USD (OTC)", 
    "MAD/USD (OTC)", "OMR/CNY (OTC)", "USD/ARC (OTC)", "USD/COP (OTC)", 
    "USD/MYR (OTC)", "ZAR/USD (OTC)", "USD/PKR (OTC)", "GBP/JPY (OTC 2)",
    
    # Предишни активи
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
    "NVIDIA (OTC)", "NETFLIX (OTC)"
]

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
    current_time = datetime.now() - timedelta(seconds=100 * tf_seconds)
    current_price = base_price
    for i in range(100):
        current_price += random.uniform(-base_price * 0.0003, base_price * 0.0003)
        prices.append(current_price)
        times.append(current_time + timedelta(seconds=i * tf_seconds))
    return pd.DataFrame({"Timestamp": times, "Price": prices})

# =====================================================================
# 3. НАСТРОЙКИ В САЙДБАРА
# =====================================================================
st.sidebar.title("🤖 Настройки")
selected_asset = st.sidebar.selectbox("Избор на актив:", all_otc_assets, index=0)
timeframe_label = st.sidebar.selectbox(
    "Таймфрейм:",
    options=["5 сек", "15 сек", "30 сек", "1 мин", "3 мин", "5 мин", "10 мин"],
    index=3
)

tf_mapping = {
    "5 сек": 5, "15 сек": 15, "30 сек": 30,
    "1 мин": 60, "3 мин": 180, "5 мин": 300, "10 мин": 600
}
tf_seconds = tf_mapping[timeframe_label]

# Регулиране на EMA спрямо секунден/минутен таймфрейм
is_seconds_tf = tf_seconds < 60
if is_seconds_tf:
    p_fast, p_mid, p_slow = 12, 24, 50
    ema_label_suffix = " (Секунден филтър)"
    volatility_threshold = 0.015
else:
    p_fast, p_mid, p_slow = 8, 14, 21
    ema_label_suffix = " (Минутен импулс)"
    volatility_threshold = 0.008

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Активни ЕМА периоди:**")
st.sidebar.text(f"Бърза: EMA {p_fast}")
st.sidebar.text(f"Средна: EMA {p_mid}")
st.sidebar.text(f"Бавна: EMA {p_slow}")

# Инициализиране/Смяна в Session State
if "current_asset" not in st.session_state or st.session_state.current_asset != selected_asset or "current_tf" not in st.session_state or st.session_state.current_tf != tf_seconds:
    st.session_state.current_asset = selected_asset
    st.session_state.current_tf = tf_seconds
    st.session_state.df_history = generate_fresh_history(selected_asset, tf_seconds)
    st.session_state.last_bucket = int(datetime.now().timestamp() / tf_seconds)

# =====================================================================
# 4. МАТЕМАТИЧЕСКИ ИЗЧИСЛЕНИЯ НА ДАННИТЕ
# =====================================================================
now = datetime.now()
current_bucket = int(now.timestamp() / tf_seconds)
remaining_seconds = tf_seconds - (int(now.timestamp()) % tf_seconds)

# Логика за добавяне/обновяване на свещ
if current_bucket != st.session_state.last_bucket:
    st.session_state.last_bucket = current_bucket
    last_price = st.session_state.df_history["Price"].iloc[-1]
    new_price = last_price + random.uniform(-last_price * 0.0003, last_price * 0.0003)
    new_row = pd.DataFrame({"Timestamp": [now], "Price": [new_price]})
    st.session_state.df_history = pd.concat([st.session_state.df_history.iloc[1:], new_row], ignore_index=True)
else:
    # Симулация на текущ тик
    last_price = st.session_state.df_history["Price"].iloc[-1]
    st.session_state.df_history.loc[st.session_state.df_history.index[-1], "Price"] = last_price + random.uniform(-last_price * 0.0001, last_price * 0.0001)

df = st.session_state.df_history.copy()

# Калкулиране на ЕМА върху текущия фрейм
df['EMA_FAST'] = df['Price'].ewm(span=p_fast, adjust=False).mean()
df['EMA_MID'] = df['Price'].ewm(span=p_mid, adjust=False).mean()
df['EMA_SLOW'] = df['Price'].ewm(span=p_slow, adjust=False).mean()

current_p = df['Price'].iloc[-1]
ema_fast_p = df['EMA_FAST'].iloc[-1]
ema_mid_p = df['EMA_MID'].iloc[-1]
ema_slow_p = df['EMA_SLOW'].iloc[-1]

# Изчисляване на волатилността (Разстояние между линиите)
ema_spread_pct = (abs(ema_fast_p - ema_slow_p) / ema_slow_p) * 100
is_low_volatility = ema_spread_pct < volatility_threshold

# =====================================================================
# 5. ВИЗУАЛИЗАЦИЯ НА ИНТЕРФЕЙСА (Основен екран)
# =====================================================================
st.title("🤖 PO 3 EMA Bot Dashboard")

# Горна линия с метрики
t_col1, t_col2, t_col3 = st.columns(3)
t_col1.metric("🕒 Текущо време", now.strftime("%H:%M:%S"))
t_col2.metric(f"⏳ Следващ вход ({timeframe_label})", f"{remaining_seconds} сек.")

fmt_str = "{:.6f}" if current_p < 0.01 else ("{:.4f}" if current_p < 1000 else "{:.2f}")
t_col3.metric(f"Цена {selected_asset}", fmt_str.format(current_p))

st.write("---")

# Анализ на пазара и определяне на сигналите
if is_low_volatility:
    buy_ratio, sell_ratio = random.randint(49, 51), random.randint(49, 51)
    arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠➡</div><div class='direction-text' style='color: #ffaa00;'>LOW VOLATILITY</div>"
    msg_type = "warning"
    status_text = f"❌ НИСКА ВОЛАТИЛНОСТ / ОПАСЕН ВХОД: Линиите са прекалено близо ({ema_spread_pct:.4f}%). Изчакайте!"
elif ema_fast_p > ema_mid_p > ema_slow_p:
    if current_p >= ema_fast_p:
        buy_ratio = random.randint(85, 96)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
        msg_type = "success"
        status_text = f"🔥 СИЛЕН ИМПУЛС: Потвърден възходящ тренд на {timeframe_label}."
    else:
        buy_ratio = random.randint(60, 70)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬆</div><div class='direction-text' style='color: #ffaa00;'>WEAK BUY</div>"
        msg_type = "warning"
        status_text = f"⏳ КОРЕКЦИЯ: Възходящ тренд, но цената падна под ЕМА {p_fast}."
elif ema_fast_p < ema_mid_p < ema_slow_p:
    if current_p <= ema_fast_p:
        sell_ratio = random.randint(85, 96)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ff3333;'>⬇</div><div class='direction-text' style='color: #ff3333;'>STRONG SELL</div>"
        msg_type = "error"
        status_text = f"🚨 СИЛЕН ИМПУЛС: Потвърден низходящ тренд на {timeframe_label}."
    else:
        sell_ratio = random.randint(60, 70)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬇</div><div class='direction-text' style='color: #ffaa00;'>WEAK SELL</div>"
        msg_type = "warning"
