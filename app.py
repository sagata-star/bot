import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta

# 1. Настройка на уеб страницата (Задължително на първия ред)
st.set_page_config(
    page_title="PO 3 EMA Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Инжектиране на компактни CSS стилове за събиране на всичко на 1 екран
st.markdown("""
    <style>
    .main { background-color: #1c1f26; color: #ffffff; }
    div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: bold; color: #00ffcc; }
    div[data-testid="stMetricLabel"] { font-size: 13px !important; color: #aaaaaa; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    h1 { font-size: 26px !important; margin-bottom: 5px !important; padding-bottom: 0px; }
    h3 { font-size: 16px !important; margin-top: 5px !important; margin-bottom: 5px !important; }
    div[data-testid="stSidebar"] { background-color: #11141a; }
    </style>
""", unsafe_allow_html=True)

# 3. --- ПЪЛЕН СПИСЪК С ВСИЧКИ OTC АКТИВИ НА POCKET OPTION ---
all_otc_assets = [
    # Основни и Крос Валутни Двойки (Forex OTC Pairs)
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "EUR/GBP (OTC)", "USD/CAD (OTC)", "NZD/USD (OTC)", "EUR/JPY (OTC)",
    "GBP/JPY (OTC)", "EUR/CAD (OTC)", "AUD/CAD (OTC)", "USD/CHF (OTC)",
    "EUR/CHF (OTC)", "CAD/JPY (OTC)", "AUD/JPY (OTC)", "CHF/JPY (OTC)",
    "GBP/CAD (OTC)", "EUR/AUD (OTC)", "AUD/CHF (OTC)", "AUD/NZD (OTC)",
    "CAD/CHF (OTC)", "EUR/NZD (OTC)", "GBP/AUD (OTC)", "GBP/CHF (OTC)",
    "GBP/NZD (OTC)", "NZD/CAD (OTC)", "NZD/CHF (OTC)", "NZD/JPY (OTC)",
    
    # Екзотични Валутни Двойки (Exotic OTC Pairs)
    "USD/TRY (OTC)", "EUR/ZAR (OTC)", "USD/ZAR (OTC)", "USD/THB (OTC)", 
    "USD/SGD (OTC)", "USD/RUB (OTC)", "EUR/RUB (OTC)", "USD/PLN (OTC)", 
    "USD/NOK (OTC)", "USD/SEK (OTC)", "USD/MXN (OTC)", "USD/INR (OTC)",
    "USD/HKD (OTC)", "USD/DKK (OTC)", "USD/CNH (OTC)", "USD/BRL (OTC)",
    "USD/ARS (OTC)", "AED/CNY (OTC)", "NGN/USD (OTC)", "KES/USD (OTC)", 
    "UAH/USD (OTC)",
    
    # Стоки, Индекси и Акции
    "GOLD (OTC)", "SILVER (OTC)", "APPLE (OTC)", "GOOGLE (OTC)", 
    "MICROSOFT (OTC)", "AMAZON (OTC)", "TESLA (OTC)", "META (OTC)", 
    "NVIDIA (OTC)", "NETFLIX (OTC)"
]

# 4. Функция за генериране на базова история без тежък кеш
def generate_fresh_history(asset_name):
    if "JPY" in asset_name: base_price = 145.25
    elif "CHF" in asset_name and "JPY" not in asset_name: base_price = 0.8950
    elif "GOLD" in asset_name: base_price = 2350.00
    elif "SILVER" in asset_name: base_price = 28.50
    elif any(x in asset_name for x in ["APPLE", "GOOGLE", "META", "NVIDIA", "NETFLIX", "TESLA", "MICROSOFT", "AMAZON"]):
        base_price = random.uniform(150.00, 450.00)
    else: base_price = 1.1234

    # Генериране на 100 точки история в реално време
    prices = []
    times = []
    current_time = datetime.now() - timedelta(minutes=100)
    current_price = base_price
    
    for i in range(100):
        current_price += random.uniform(-base_price * 0.0005, base_price * 0.0005)
        prices.append(current_price)
        times.append(current_time + timedelta(minutes=i))
        
    return pd.DataFrame({"Timestamp": times, "Price": prices})

# 5. ИНТЕРФЕЙС - ЗАГЛАВИЕ И СТРАНИЧЕН ПАНЕЛ (Всичко на 1 страница)
st.title("🤖 PO 3 EMA Bot Dashboard")

# Страничен избор на актив
selected_asset = st.sidebar.selectbox("Избор на актив:", all_otc_assets, index=0)
refresh_rate = st.sidebar.slider("Опресняване (секунди):", min_value=1, max_value=10, value=2)

# Вземане на данни
df = generate_fresh_history(selected_asset)

# Изчисляване на 3-те ЕМА линии
df['EMA_8'] = df['Price'].ewm(span=8, adjust=False).mean()
df['EMA_14'] = df['Price'].ewm(span=14, adjust=False).mean()
df['EMA_21'] = df['Price'].ewm(span=21, adjust=False).mean()

# 6. КОМПАКТНИ МЕТРИКИ (Най-отгоре на същата страница)
col1, col2, col3, col4 = st.columns(4)
current_p = df['Price'].iloc[-1]
ema8_p = df['EMA_8'].iloc[-1]
ema14_p = df['EMA_14'].iloc[-1]
ema21_p = df['EMA_21'].iloc[-1]

col1.metric(label=f"Цена {selected_asset}", value=f"{current_p:.4f}")
col2.metric(label="EMA 8 (Бърза)", value=f"{ema8_p:.4f}")
col3.metric(label="EMA 14 (Средна)", value=f"{ema14_p:.4f}")
col4.metric(label="EMA 21 (Бавна)", value=f"{ema21_p:.4f}")

# Логика за сигнал BUY / SELL
st.write("---")
if ema8_p > ema14_p > ema21_p:
    st.success("🔥 СИГНАЛ: СИЛЕН BUY (ВЪЗХОДЯЩ ТРЕНД)")
elif ema8_p < ema14_p < ema21_p:
    st.error("🚨 СИГНАЛ: СИЛЕН SELL (НИСХОДЯЩ ТРЕНД)")
else:
    st.warning("⏳ СИГНАЛ: СТРАНИЧНО ДВИЖЕНИЕ / ИЗЧАКВАНЕ")

# 7. ГРАФИКА НА СЪЩАТА СТРАНИЦА
st.subheader("Визуализация на 3 EMA Тренд")
chart_data = df.set_index("Timestamp")[["Price", "EMA_8", "EMA_14", "EMA_21"]]
st.line_chart(chart_data, height=400)

# Автоматично опресняване без чупене на браузъра
time.sleep(refresh_rate)
st.rerun()
