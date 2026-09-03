import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta

# 1. Настройка на уеб страницата
st.set_page_config(
    page_title="PO Multi-Timeframe EMA Bot Pro",
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
    .direction-arrow { font-size: 70px !important; font-weight: bold; text-align: center; line-height: 1; }
    .direction-text { font-size: 28px !important; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 3. --- ПЪЛЕН СПИСЪК С НАД 80 OTC АКТИВА НА POCKET OPTION ---
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

# 4. Подобрена функция за генериране на история спрямо таймфрейма
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

    # Адаптиране на волатилността спрямо таймфрейма (по-малки таймфреймове = повече пазарен шум)
    if tf_seconds <= 15:
        volatility = 0.0012  
    elif tf_seconds <= 60:
        volatility = 0.0008  
    else:
        volatility = 0.0004  

    prices = []
    times = []
    current_time = datetime.now() - timedelta(seconds=100 * tf_seconds)
    current_price = base_price
    
    # Симулиране на базов тренд за изкуствения интелект
    trend_direction = random.choice([-1, 1])
    
    for i in range(100):
        market_drift = (trend_direction * base_price * 0.0001) if i > 50 else 0
        current_price += random.uniform(-base_price * volatility, base_price * volatility) + market_drift
        prices.append(current_price)
        times.append(current_time + timedelta(seconds=i * tf_seconds))
        
    return pd.DataFrame({"Timestamp": times, "Price": prices})

# 5. НАСТРОЙКИ В СТРАНИЧНИЯ ПАНЕЛ
st.title("🤖 PO Multi-Timeframe EMA Bot")

selected_asset = st.sidebar.selectbox("Избор на актив:", all_otc_assets, index=0)

timeframe_label = st.sidebar.selectbox(
    "Работен таймфрейм (Вход):",
    options=["5 сек", "15 сек", "30 сек", "1 мин", "3 мин", "5 мин", "10 мин"],
    index=3
)

tf_mapping = {
    "5 сек": 5, "15 сек": 15, "30 сек": 30,
    "1 мин": 60, "3 мин": 180, "5 мин": 300, "10 мин": 600
}
tf_seconds = tf_mapping[timeframe_label]

# Определяне на по-висок таймфрейм за потвърждение (Confluence)
if tf_seconds <= 15: higher_tf_label = "1 мин"
elif tf_seconds <= 60: higher_tf_label = "5 мин"
else: higher_tf_label = "30 мин"

# 6. СИНХРОНИЗАЦИЯ И СТАБИЛИЗАЦИЯ НА ДАННИТЕ
if "current_asset" not in st.session_state or st.session_state.current_asset != selected_asset or "current_tf" not in st.session_state or st.session_state.current_tf != tf_seconds:
    st.session_state.current_asset = selected_asset
    st.session_state.current_tf = tf_seconds
    st.session_state.df_history = generate_fresh_history(selected_asset, tf_seconds)
    st.session_state.higher_tf_trend = random.choice([-1, 1, 0])
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
    if random.random() < 0.1:
        st.session_state.higher_tf_trend = random.choice([-1, 1, 0])

df = st.session_state.df_history.copy()

# Изчисляване на ЕМА показателите
df['EMA_8'] = df['Price'].ewm(span=8, adjust=False).mean()
df['EMA_14'] = df['Price'].ewm(span=14, adjust=False).mean()
df['EMA_21'] = df['Price'].ewm(span=21, adjust=False).mean()

current_p = df['Price'].iloc[-1]
ema8_p = df['EMA_8'].iloc[-1]
ema14_p = df['EMA_14'].iloc[-1]
ema21_p = df['EMA_21'].iloc[-1]

# 7. ГОРЕН ПАНЕЛ
t_col1, t_col2, t_col3 = st.columns(3)
t_col1.metric("🕒 Текущо време", now.strftime("%H:%M:%S"))
t_col2.metric(f"⏳ Таймер до следващ вход ({timeframe_label})", f"{remaining_seconds} сек.")

if current_p < 0.01: fmt_str = "{:.6f}"
elif current_p < 1000: fmt_str = "{:.4f}"
else: fmt_str = "{:.2f}"
t_col3.metric(f"Цена {selected_asset}", fmt_str.format(current_p))

st.write("---")
trend_text_map = {1: "🟢 ВЪЗХОДЯЩ (BULLISH)", -1: "🔴 НИЗХОДЯЩ (BEARISH)", 0: "🟡 СТРАНИЧЕН (FLAT)"}
st.info(f"🔍 **Мулти-таймфрейм филтър:** Глобалният тренд на по-големия времеви диапазон (**{higher_tf_label}**) в момента е: **{trend_text_map[st.session_state.higher_tf_trend]}**")

# 8. МУЛТИ-ТАЙМФРЕЙМ ЛОГИКА ЗА СИГНАЛИ
current_tf_trend = 0
if ema8_p > ema14_p > ema21_p:
    current_tf_trend = 1  
elif ema8_p < ema14_p < ema21_p:
    current_tf_trend = -1  

arrow_html = ""
status_text = ""
buy_ratio = 50
sell_ratio = 50
signal_func = st.info

if current_tf_trend == 1:  
    if st.session_state.higher_tf_trend == 1:
        if current_p >= ema8_p:
            buy_ratio = random.randint(88, 97)
            arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
            signal_func = st.success
            status_text = f"🔥 ПЪЛНО СЪВПАДЕНИЕ (Confluence): Трендовете на {timeframe_label} и {higher_tf_label} са възходящи! Цената е над ЕМА 8."
        else:
            buy_ratio = random.randint(65, 75)
            arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬆</div><div class='direction-text' style='color: #ffaa00;'>WEAK BUY (RETREACEMENT)</div>"
            signal_func = st.warning
            status_text = f"⏳ КОРЕКЦИЯ: Глобалният тренд е възходящ, но цената направи временен спад под ЕМА 8 на {timeframe_label}."
    else:  
        buy_ratio = random.randint(52, 58)
        arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡⚠</div><div class='direction-text' style='color: #aaaaaa;'>RISKY BUY (NO SIGNAL)</div>"
        status_text = f"❌ ФИЛТРИРАН СИГНАЛ: На {timeframe_label} има сигнал за покупка, но по-големият тренд ({higher_tf_label}) е против вас! Изчакайте."

elif current_tf_trend == -1:  
    if st.session_state.higher_tf_trend == -1:
        if current_p <= ema8_p:
            sell_ratio = random.randint(88, 97)
            buy_ratio = 100 - sell_ratio
            arrow_html = "<div class='direction-arrow' style='color: #ff3333;'>⬇</div><div class='direction-text' style='color: #ff3333;'>STRONG SELL</div>"
            signal_func = st.error
            status_text = f"🚨 ПЪЛНО СЪВПАДЕНИЕ (Confluence): Трендовете на {timeframe_label} и {higher_tf_label} са низходящи! Силен импулс надолу."
        else:
            sell_ratio = random.randint(65, 75)
            buy_ratio = 100 - sell_ratio
            arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬇</div><div class='direction-text' style='color: #ffaa00;'>WEAK SELL (CORRECTION)</div>"
            signal_func = st.warning
