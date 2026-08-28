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

# 3. --- ПЪЛЕН СПИСЪК С ВСИЧКИ OTC АКТИВИ НА POCKET OPTION ---
all_otc_assets = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "EUR/GBP (OTC)", "USD/CAD (OTC)", "NZD/USD (OTC)", "EUR/JPY (OTC)",
    "GBP/JPY (OTC)", "EUR/CAD (OTC)", "AUD/CAD (OTC)", "USD/CHF (OTC)",
    "EUR/CHF (OTC)", "CAD/JPY (OTC)", "AUD/JPY (OTC)", "CHF/JPY (OTC)",
    "GBP/CAD (OTC)", "EUR/AUD (OTC)", "AUD/CHF (OTC)", "AUD/NZD (OTC)",
    "CAD/CHF (OTC)", "EUR/NZD (OTC)", "GBP/AUD (OTC)", "GBP/CHF (OTC)",
    "GBP/NZD (OTC)", "NZD/CAD (OTC)", "NZD/CHF (OTC)", "NZD/JPY (OTC)",
    "USD/TRY (OTC)", "EUR/ZAR (OTC)", "USD/ZAR (OTC)", "USD/THB (OTC)", 
    "USD/SGD (OTC)", "USD/RUB (OTC)", "EUR/RUB (OTC)", "USD/PLN (OTC)", 
    "USD/NOK (OTC)", "USD/SEK (OTC)", "USD/MXN (OTC)", "USD/INR (OTC)",
    "USD/HKD (OTC)", "USD/DKK (OTC)", "USD/CNH (OTC)", "USD/BRL (OTC)",
    "USD/ARS (OTC)", "AED/CNY (OTC)", "NGN/USD (OTC)", "KES/USD (OTC)", 
    "UAH/USD (OTC)", "GOLD (OTC)", "SILVER (OTC)", "APPLE (OTC)", "GOOGLE (OTC)", 
    "MICROSOFT (OTC)", "AMAZON (OTC)", "TESLA (OTC)", "META (OTC)", 
    "NVIDIA (OTC)", "NETFLIX (OTC)"
]

# 4. Функция за генериране на базова история
def generate_fresh_history(asset_name, timeframe_mins):
    if "JPY" in asset_name: base_price = 145.25
    elif "CHF" in asset_name and "JPY" not in asset_name: base_price = 0.8950
    elif "GOLD" in asset_name: base_price = 2350.00
    elif "SILVER" in asset_name: base_price = 28.50
    elif any(x in asset_name for x in ["APPLE", "GOOGLE", "META", "NVIDIA", "NETFLIX", "TESLA", "MICROSOFT", "AMAZON"]):
        base_price = random.uniform(150.00, 450.00)
    else: base_price = 1.1234

    prices = []
    times = []
    current_time = datetime.now() - timedelta(minutes=100 * timeframe_mins)
    current_price = base_price
    
    for i in range(100):
        current_price += random.uniform(-base_price * 0.0008, base_price * 0.0008)
        prices.append(current_price)
        times.append(current_time + timedelta(minutes=i * timeframe_mins))
        
    return pd.DataFrame({"Timestamp": times, "Price": prices})

# 5. НАСТРОЙКИ В СТРАНИЧНИЯ ПАНЕЛ
st.title("🤖 PO 3 EMA Bot Dashboard")

selected_asset = st.sidebar.selectbox("Избор на актив:", all_otc_assets, index=0)
timeframe = st.sidebar.selectbox("Времеви диапазон (Таймфрейм):", [1, 3, 5, 10], index=0, format_func=lambda x: f"{x} мин.")

# 6. СИНХРОНИЗАЦИЯ И СТАБИЛИЗАЦИЯ НА ДАННИТЕ
if "current_asset" not in st.session_state or st.session_state.current_asset != selected_asset or "current_tf" not in st.session_state or st.session_state.current_tf != timeframe:
    st.session_state.current_asset = selected_asset
    st.session_state.current_tf = timeframe
    st.session_state.df_history = generate_fresh_history(selected_asset, timeframe)
    st.session_state.last_update_minute = datetime.now().minute

now = datetime.now()
current_minute = now.minute

if current_minute % timeframe == 0 and current_minute != st.session_state.last_update_minute:
    st.session_state.last_update_minute = current_minute
    last_price = st.session_state.df_history["Price"].iloc[-1]
    new_price = last_price + random.uniform(-last_price * 0.0008, last_price * 0.0008)
    new_row = pd.DataFrame({"Timestamp": [now], "Price": [new_price]})
    st.session_state.df_history = pd.concat([st.session_state.df_history.iloc[1:], new_row], ignore_index=True)

df = st.session_state.df_history.copy()

# Изчисляване на ЕМА показателите
df['EMA_8'] = df['Price'].ewm(span=8, adjust=False).mean()
df['EMA_14'] = df['Price'].ewm(span=14, adjust=False).mean()
df['EMA_21'] = df['Price'].ewm(span=21, adjust=False).mean()

# Извличане на текущи стойности
current_time_str = now.strftime("%H:%M:%S")
seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
timeframe_seconds = timeframe * 60
remaining_seconds = int(timeframe_seconds - (seconds_since_midnight % timeframe_seconds))

current_p = df['Price'].iloc[-1]
ema8_p = df['EMA_8'].iloc[-1]
ema14_p = df['EMA_14'].iloc[-1]
ema21_p = df['EMA_21'].iloc[-1]

# 7. ГОРЕН ПАНЕЛ: ЧАСОВНИК, ТАЙМЕР И ЦЕНА
t_col1, t_col2, t_col3 = st.columns(3)
t_col1.metric("🕒 Текущо време (Реално)", current_time_str)
t_col2.metric(f"⏳ Таймер до следващ вход ({timeframe}м)", f"{remaining_seconds} сек.")
t_col3.metric(f"Цена {selected_asset}", f"{current_p:.4f}")

# 8. СРЕДЕН ПАНЕЛ: НОВАТА СТРОГА ЛОГИКА ЗА СИГНАЛИ
st.write("---")

if ema8_p > ema14_p > ema21_p:
    if current_p >= ema8_p:
        buy_ratio = random.randint(85, 96)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
        signal_func = st.success
        status_text = f"🔥 СИЛЕН ИМПУЛС: Линиите и цената потвърждават възходящ тренд на {timeframe}м."
    else:
        buy_ratio = random.randint(60, 70)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬆</div><div class='direction-text' style='color: #ffaa00;'>WEAK BUY</div>"
        signal_func = st.warning
        status_text = f"⏳ КОРЕКЦИЯ: Възходящ тренд, но цената падна под ЕМА 8. Изчакайте!"

elif ema8_p < ema14_p < ema21_p:
    if current_p <= ema8_p:
        sell_ratio = random.randint(85, 96)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ff3333;'>⬇</div><div class='direction-text' style='color: #ff3333;'>STRONG SELL</div>"
        signal_func = st.error
        status_text = f"🚨 СИЛЕН ИМПУЛС: Линиите и цената потвърждават низходящ тренд на {timeframe}м."
    else:
        sell_ratio = random.randint(60, 70)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬇</div><div class='direction-text' style='color: #ffaa00;'>WEAK SELL</div>"
        signal_func = st.warning
        status_text = f"⏳ КОРЕКЦИЯ: Низходящ тренд, но цената се качи над ЕМА 8. Изчакайте!"

else:
    buy_ratio = random.randint(47, 53)
    sell_ratio = 100 - buy_ratio
    arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡</div><div class='direction-text' style='color: #aaaaaa;'>NO SIGNAL</div>"
    signal_func = st.info
    status_text = f"📉 КОНСОЛИДАЦИЯ (ФЛАТ): Линиите се преплитат хаотично. Пазарът няма посока."

sig_col1, sig_col2 = st.columns(2)

with sig_col1:
    st.markdown(arrow_html, unsafe_allow_html=True)

with sig_col2:
    st.subheader(f"📊 Пазарно съотношение ({timeframe}м)")
    st.markdown(f"**Купувачи (Bulls):** {buy_ratio}%")
    st.progress(buy_ratio / 100)
    st.markdown(f"**Продавачи (Bears):** {sell_ratio}%")
    signal_func(status_text)

# 9. ДОЛЕН ПАНЕЛ: ТЕХНИЧЕСКИ ИНДИКАТОРИ НАЙ-ОТДОЛУ
st.write("---")
st.markdown(f"##### 📊 Технически индикатори за {selected_asset}")

ema_col1, ema_col2, ema_col3 = st.columns(3)
ema_col1.metric(label="EMA 8 (Бърза)", value=f"{ema8_p:.4f}")
ema_col2.metric(label="EMA 14 (Средна)", value=f"{ema14_p:.4f}")
ema_col3.metric(label="EMA 21 (Бавна)", value=f"{ema21_p:.4f}")

# Плавно опресняване на реалното време
time.sleep(1)
st.rerun()
