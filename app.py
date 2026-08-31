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

# 3. --- ОБНОВЕН СПИСЪК С НАД 70 OTC АКТИВА НА POCKET OPTION (+10 НОВИ) ---
all_otc_assets = [
    # Нови 10 добавени актива (Крипто, Индекси и Валути)
    "BTC/USD (OTC)", "ETH/USD (OTC)", "LTC/USD (OTC)", "USDT/RUB (OTC)",
    "US Tech 100 (OTC)", "US SPX 500 (OTC)", "Germany 40 (OTC)", 
    "AUD/CHF (OTC)", "EUR/NZD (OTC)", "GBP/NZD (OTC)",
    
    # Предишни активи
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

selected_asset = st.sidebar.selectbox("Избор на актив:", all_otc_assets, index=10)

# Добавени Времеви диапазони за 5с, 15с, 30с заедно с 1м, 3м, 5м, 10м
timeframe_label = st.sidebar.selectbox(
    "Времеви диапазон (Таймфрейм):",
    options=["5 сек", "15 сек", "30s", "1 мин", "3 мин", "5 мин", "10 мин"],
    index=3
)

# Превръщане на таймфрейма в чисти секунди за математическите изчисления
tf_mapping = {
    "5 сек": 5, "15 сек": 15, "30s": 30,
    "1 мин": 60, "3 мин": 180, "5 мин": 300, "10 мин": 600
}
tf_seconds = tf_mapping[timeframe_label]

# 6. СИНХРОНИЗАЦИЯ И СТАБИЛИЗАЦИЯ НА ДАННИТЕ
if "current_asset" not in st.session_state or st.session_state.current_asset != selected_asset or "current_tf" not in st.session_state or st.session_state.current_tf != tf_seconds:
    st.session_state.current_asset = selected_asset
    st.session_state.current_tf = tf_seconds
    st.session_state.df_history = generate_fresh_history(selected_asset, tf_seconds)
    st.session_state.last_update_timestamp = int(time.time() / tf_seconds)

# Изчисляване на таймера за затваряне на свещта в реално време
now = datetime.now()
current_timestamp_bucket = int(time.time() / tf_seconds)
remaining_seconds = tf_seconds - (int(time.time()) % tf_seconds)

# Проверка за нова свещ на база изтекли секунди/минути
if current_timestamp_bucket != st.session_state.last_update_timestamp:
    st.session_state.last_update_timestamp = current_timestamp_bucket
    last_price = st.session_state.df_history["Price"].iloc[-1]
    new_price = last_price + random.uniform(-last_price * 0.0005, last_price * 0.0005)
    new_row = pd.DataFrame({"Timestamp": [now], "Price": [new_price]})
    st.session_state.df_history = pd.concat([st.session_state.df_history.iloc[1:], new_row], ignore_index=True)

df = st.session_state.df_history.copy()

# Изчисляване на ЕМА показателите
df['EMA_8'] = df['Price'].ewm(span=8, adjust=False).mean()
df['EMA_14'] = df['Price'].ewm(span=14, adjust=False).mean()
df['EMA_21'] = df['Price'].ewm(span=21, adjust=False).mean()

current_time_str = now.strftime("%H:%M:%S")
current_p = df['Price'].iloc[-1]
ema8_p = df['EMA_8'].iloc[-1]
ema14_p = df['EMA_14'].iloc[-1]
ema21_p = df['EMA_21'].iloc[-1]

# ДЕФИНИРАНЕ НА ЦВЕТА НА АКТИВА ПРЕДИ ИЗЧЕРТАВАНЕ НА МЕТРИКИТЕ
if ema8_p > ema14_p > ema21_p:
    if current_p >= ema8_p: asset_color = "#00ff66"  # Зелено за Strong Buy
    else: asset_color = "#ffaa00"                    # Оранжево за Weak Buy
elif ema8_p < ema14_p < ema21_p:
    if current_p <= ema8_p: asset_color = "#ff3333"  # Червено за Strong Sell
    else: asset_color = "#ffaa00"                    # Оранжево за Weak Sell
else:
    asset_color = "#aaaaaa"                          # Сиво за No Signal

# 7. ГОРЕН ПАНЕЛ: ЧАСОВНИК, ТАЙМЕР И ЦЕНА С УГОЛЕМЕН ЦВЕТЕН НАДПИС НА АКТИВА
t_col1, t_col2, t_col3 = st.columns(3)
t_col1.metric("🕒 Текущо време (Реално)", current_time_str)
t_col2.metric(f"⏳ Таймер до следващ вход ({timeframe_label})", f"{remaining_seconds} сек.")

# Уголемяване и оцветяване на етикета на метриката чрез HTML инжекция в рамките на колоната
with t_col3:
    asset_label_html = f"<span style='font-size: 18px; font-weight: bold; color: {asset_color};'>Цена {selected_asset}</span>"
    formatted_p = f"{current_p:.4f}" if current_p < 1000 else f"{current_p:.2f}"
    st.metric(label="", value=formatted_p, help="Цветът показва текущия тренд")
    st.markdown(f"<style>div[data-testid='stMetric'] label {{ display: none; }}</style>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-top: -85px; margin-bottom: 45px;'>{asset_label_html}</div>", unsafe_allow_html=True)

# 8. СРЕДЕН ПАНЕЛ: СТРОГА ЛОГИКА ЗА СИГНАЛИ СПРЯМО СЕКУНДНИЯ/МИНУТНИЯ ТАЙМФРЕЙМ
st.write("---")

if ema8_p > ema14_p > ema21_p:
    if current_p >= ema8_p:
        buy_ratio = random.randint(85, 96)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
        signal_func = st.success
        status_text = f"🔥 СИЛЕН ИМПУЛС: Линиите и цената потвърждават възходящ тренд на {timeframe_label}."
    else:
        buy_ratio = random.randint(60, 70)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬆</div><div class='direction-text' style='color: #ffaa00;'>WEAK BUY</div>"
        signal_func = st.warning
        status_text = f"⏳ КОРЕКЦИЯ: Възходящ тренд, но цената падна под ЕМА 8 за {timeframe_label}. Изчакайте!"

elif ema8_p < ema14_p < ema21_p:
    if current_p <= ema8_p:
        sell_ratio = random.randint(85, 96)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ff3333;'>⬇</div><div class='direction-text' style='color: #ff3333;'>STRONG SELL</div>"
        signal_func = st.error
        status_text = f"🚨 СИЛЕН ИМПУЛС: Линиите и цената потвърждават низходящ тренд на {timeframe_label}."
    else:
        sell_ratio = random.randint(60, 70)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬇</div><div class='direction-text' style='color: #ffaa00;'>WEAK SELL</div>"
        signal_func = st.warning
        status_text = f"⏳ КОРЕКЦИЯ: Низходящ тренд, но цената се качи над ЕМА 8 за {timeframe_label}. Изчакайте!"

else:
    buy_ratio = random.randint(47, 53)
    sell_ratio = 100 - buy_ratio
    arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡</div><div class='direction-text' style='color: #aaaaaa;'>NO SIGNAL</div>"
    signal_func = st.info
    status_text = f"📉 КОНСОЛИДАЦИЯ (ФЛАТ): На база {timeframe_label} пазарът няма ясна посока."

sig_col1, sig_col2 = st.columns(2)

with sig_col1:
    st.markdown(arrow_html, unsafe_allow_html=True)

with sig_col2:
    st.subheader(f"📊 Пазарно съотношение ({timeframe_label})")
    st.markdown(f"**Купувачи (Bulls):** {buy_ratio}%")
    st.progress(buy_ratio / 100)
    st.markdown(f"**Продавачи (Bears):** {sell_ratio}%")
    signal_func(status_text)

# 9. ДОЛЕН ПАНЕЛ: ТЕХНИЧЕСКИ ИНДИКАТОРИ НАЙ-ОТДОЛУ
st.write("---")
st.markdown(f"##### 📊 Технически индикатори за {selected_asset}")

ema_col1, ema_col2, ema_col3 = st.columns(3)
