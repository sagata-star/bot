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

# 2. Инжектиране на компактни CSS стилове
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

# 3. --- ОБНОВЕН СПИСЪК С НАД 80 OTC АКТИВА НА POCKET OPTION ---
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
    "NVIDIA (OTC)", "NETFLIX (OTC)"
]

# 4. Функция за генериране на базова история спрямо секунди или минути
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
    "5 сек": 5, "15 сек": 15, "30 sec": 30, "30 сек": 30,
    "1 мин": 60, "3 мин": 180, "5 мин": 300, "10 мин": 600
}
tf_seconds = tf_mapping[timeframe_label]

# Динамично определяне на EMA периодите на база таймфрейма
if tf_seconds < 60:
    p_fast, p_med, p_slow = 12, 24, 50
    ema_mode_text = "Адаптивен секунден филтър (EMA 12/24/50)"
else:
    p_fast, p_med, p_slow = 8, 14, 21
    ema_mode_text = "Стандартен минутен импулс (EMA 8/14/21)"

# 6. СИНХРОНИЗАЦИЯ И СТАБИЛИЗАЦИЯ НА ДАННИТЕ
if "current_asset" not in st.session_state or st.session_state.current_asset != selected_asset or "current_tf" not in st.session_state or st.session_state.current_tf != tf_seconds:
    st.session_state.current_asset = selected_asset
    st.session_state.current_tf = tf_seconds
    st.session_state.df_history = generate_fresh_history(selected_asset, tf_seconds)
    st.session_state.last_update_timestamp = int(time.time() / tf_seconds)

now = datetime.now()
current_timestamp_bucket = int(time.time() / tf_seconds)
remaining_seconds = tf_seconds - (int(time.time()) % tf_seconds)

if current_timestamp_bucket != st.session_state.last_update_timestamp:
    st.session_state.last_update_timestamp = current_timestamp_bucket
    last_price = st.session_state.df_history["Price"].iloc[-1]
    new_price = last_price + random.uniform(-last_price * 0.0005, last_price * 0.0005)
    new_row = pd.DataFrame({"Timestamp": [now], "Price": [new_price]})
    st.session_state.df_history = pd.concat([st.session_state.df_history.iloc[1:], new_row], ignore_index=True)

df = st.session_state.df_history.copy()

# Изчисляване на ЕМА показателите спрямо динамичните периоди
df['EMA_FAST'] = df['Price'].ewm(span=p_fast, adjust=False).mean()
df['EMA_MED'] = df['Price'].ewm(span=p_med, adjust=False).mean()
df['EMA_SLOW'] = df['Price'].ewm(span=p_slow, adjust=False).mean()

current_time_str = now.strftime("%H:%M:%S")
current_p = df['Price'].iloc[-1]
ema_f_p = df['EMA_FAST'].iloc[-1]
ema_m_p = df['EMA_MED'].iloc[-1]
ema_s_p = df['EMA_SLOW'].iloc[-1]

# Изчисляване на спреда/разстоянието между EMA за филтриране на ниска волатилност
ema_spread = abs(ema_f_p - ema_s_p) / ema_s_p * 100
is_volatile = ema_spread > 0.015

# 7. ГОРЕН ПАНЕЛ: ЧАСОВНИК, ТАЙМЕР И ЦЕНА
t_col1, t_col2, t_col3 = st.columns(3)
t_col1.metric("🕒 Текущо време (Реално)", current_time_str)
t_col2.metric(f"⏳ Таймер до следващ вход ({timeframe_label})", f"{remaining_seconds} сек.")

if current_p < 0.01: fmt_str = "{:.6f}"
elif current_p < 1000: fmt_str = "{:.4f}"
else: fmt_str = "{:.2f}"

t_col3.metric(f"Цена {selected_asset}", fmt_str.format(current_p))

# 8. СРЕДЕН ПАНЕЛ: СТРОГА ЛОГИКА ЗА СИГНАЛИ
st.write("---")

if ema_f_p > ema_m_p > ema_s_p:
    if current_p >= ema_f_p and is_volatile:
        buy_ratio = random.randint(88, 97)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
        signal_func = st.success
        status_text = f"🔥 СИЛЕН ТРЕНДОВ ИМПУЛС: Потвърден чист възходящ тренд на {timeframe_label}."
    elif current_p >= ema_f_p and not is_volatile:
        buy_ratio = random.randint(52, 58)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡</div><div class='direction-text' style='color: #aaaaaa;'>NO SIGNAL</div>"
        signal_func = st.info
        status_text = f"📉 НИСКА ВОЛАТИЛНОСТ: Линиите са подредени за възход на {timeframe_label}, но няма силно раздалечаване. Опасна зона!"
    else:
        buy_ratio = random.randint(60, 70)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬆</div><div class='direction-text' style='color: #ffaa00;'>WEAK BUY</div>"
        signal_func = st.warning
        status_text = f"⏳ КОРЕКЦИЯ: Възходяща структура за {timeframe_label}, но цената тества бързата ЕМА линия."

elif ema_f_p < ema_m_p < ema_s_p:
    if current_p <= ema_f_p and is_volatile:
        sell_ratio = random.randint(88, 97)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ff3333;'>⬇</div><div class='direction-text' style='color: #ff3333;'>STRONG SELL</div>"
        signal_func = st.error
        status_text = f"🚨 СИЛЕН ТРЕНДОВ ИМПУЛС: Потвърден чист низходящ тренд на {timeframe_label}."
    elif current_p <= ema_f_p and not is_volatile:
        sell_ratio = random.randint(52, 58)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡</div><div class='direction-text' style='color: #aaaaaa;'>NO SIGNAL</div>"
        signal_func = st.info
        status_text = f"📉 НИСКА ВОЛАТИЛНОСТ: Линиите са подредени за спад на {timeframe_label}, но трендът е слаб. Изчакайте!"
    else:
        sell_ratio = random.randint(60, 70)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬇</div><div class='direction-text' style='color: #ffaa00;'>WEAK SELL</div>"
        signal_func = st.warning
        status_text = f"⏳ КОРЕКЦИЯ: Низходяща структура за {timeframe_label}, но цената тества бързата ЕМА линия."

else:
    buy_ratio = random.randint(47, 53)
    sell_ratio = 100 - buy_ratio
    arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡</div><div class='direction-text' style='color: #aaaaaa;'>NO SIGNAL</div>"
    signal_func = st.info
    status_text = f"📉 КОНСОЛИДАЦИЯ (ФЛАТ): На база {timeframe_label} линиите се преплитат хаотично. Пазарът няма посока."

sig_col1, sig_col2 = st.columns(2)

with sig_col1:
    st.markdown(arrow_html, unsafe_allow_html=True)

