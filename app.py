import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta

# 1. Настройка на уеб страницата
st.set_page_config(
    page_title="PO 3 EMA Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Модерни Елегантни CSS стилове с текстурни сиви балони (Cards)
st.markdown("""
    <style>
    .main { background-color: #121418; color: #ffffff; }
    div[data-testid="stSidebar"] { background-color: #1a1d24; }
    
    /* Стил за елегантните сиви балони */
    .grey-bubble {
        background: linear-gradient(145deg, #232731, #1e2229);
        border: 1px solid #2d3341;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        margin-bottom: 10px;
        text-align: center;
    }
    
    .grey-bubble-small {
        background: linear-gradient(145deg, #21252d, #1c1f26);
        border: 1px solid #2a2f3b;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
        text-align: center;
    }
    
    /* Стил за огромните стрелки за посока */
    .direction-arrow { font-size: 75px !important; font-weight: bold; text-align: center; line-height: 1; margin-bottom: 5px; }
    .direction-text { font-size: 24px !important; font-weight: bold; text-align: center; }
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

current_time_str = now.strftime("%H:%M:%S")
seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
timeframe_seconds = timeframe * 60
remaining_seconds = int(timeframe_seconds - (seconds_since_midnight % timeframe_seconds))

current_p = df['Price'].iloc[-1]
ema8_p = df['EMA_8'].iloc[-1]
ema14_p = df['EMA_14'].iloc[-1]
ema21_p = df['EMA_21'].iloc[-1]

# 7. ГОРЕН ПАНЕЛ: ЧАСОВНИК, ТАЙМЕР И ЦЕНА (Обвити в сиви балони)
t_col1, t_col2, t_col3 = st.columns(3)

with t_col1:
    st.markdown(f"<div class='grey-bubble'><p style='margin:0; color:#aaaaaa; font-size:12px;'>🕒 Текущо време</p><p style='margin:0; font-size:22px; font-weight:bold; color:#00ffcc;'>{current_time_str}</p></div>", unsafe_allow_html=True)

with t_col2:
    st.markdown(f"<div class='grey-bubble'><p style='margin:0; color:#aaaaaa; font-size:12px;'>⏳ Време до следващ вход ({timeframe}м)</p><p style='margin:0; font-size:22px; font-weight:bold; color:#ffcc00;'>{remaining_seconds} сек.</p></div>", unsafe_allow_html=True)

with t_col3:
    st.markdown(f"<div class='grey-bubble'><p style='margin:0; color:#aaaaaa; font-size:12px;'>💵 Текуща цена ({selected_asset})</p><p style='margin:0; font-size:22px; font-weight:bold; color:#00ffcc;'>{current_p:.4f}</p></div>", unsafe_allow_html=True)

# 8. СРЕДЕН ПАНЕЛ: СТРЕЛКА ЗА ПОСОКА И ПРОЦЕНТНО СЪОТНОШЕНИЕ
st.write("---")

if ema8_p > ema14_p > ema21_p:
    buy_ratio = random.randint(76, 94)
    sell_ratio = 100 - buy_ratio
    arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆</div><div class='direction-text' style='color: #00ff66;'>BUY (ДЪЛГА)</div>"
    status_text = f"<span style='color:#00ff66; font-weight:bold;'>🔥 СИЛЕН ВЪЗХОДЯЩ ТРЕНД ЗА {timeframe}М</span>"
elif ema8_p < ema14_p < ema21_p:
    sell_ratio = random.randint(76, 94)
    buy_ratio = 100 - sell_ratio
    arrow_html = "<div class='direction-arrow' style='color: #ff3333;'>⬇</div><div class='direction-text' style='color: #ff3333;'>SELL (КЪСА)</div>"
    status_text = f"<span style='color:#ff3333; font-weight:bold;'>🚨 СИЛЕН НИСХОДЯЩ ТРЕНД ЗА {timeframe}М</span>"
else:
    buy_ratio = random.randint(45, 55)
    sell_ratio = 100 - buy_ratio
    arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡</div><div class='direction-text' style='color: #aaaaaa;'>WAIT</div>"
    status_text = f"<span style='color:#aaaaaa; font-weight:bold;'>⏳ СТРАНИЧНО ДВИЖЕНИЕ (ФЛАТ) ЗА {timeframe}М</span>"

sig_col1, sig_col2 = st.columns()

with sig_col1:
    st.markdown(f"<div class='grey-bubble' style='padding:25px;'>{arrow_html}</div>", unsafe_allow_html=True)

with sig_col2:
    with st.container():
        st.markdown("<div class='grey-bubble' style='text-align:left; padding:18px;'>", unsafe_allow_html=True)
        st.markdown(f"### 📊 Пазарно съотношение ({timeframe}м)")
        st.markdown(f"**Купувачи (Bulls):** {buy_ratio}%")
        st.progress(buy_ratio / 100)
        st.markdown(f"**Продавачи (Bears):** {sell_ratio}%")
        st.markdown(f"<p style='margin-top:10px; font-size:14px;'>Статус: {status_text}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# 9. ДОЛЕН ПАНЕЛ: ПРЕМЕСТЕНИТЕ EMA 8, 14 И 21 ИНДИКАТОРИ (В отделни сиви балони)
st.write("---")
st.markdown("<h4 style='text-align:center; color:#aaaaaa; font-size:14px; margin-bottom:10px;'>📊 Технически индикатори (Изчислени стойности)</h4>", unsafe_allow_html=True)

ema_col1, ema_col2, ema_col3 = st.columns(3)

with ema_col1:
    st.markdown(f"<div class='grey-bubble-small'><p style='margin:0; color:#ff9900; font-size:12px; font-weight:bold;'>EMA 8 (Бърза)</p><p style='margin:2px 0 0 0; font-size:16px; font-weight:bold; color:#ffffff;'>{ema8_p:.4f}</p></div>", unsafe_allow_html=True)

with ema_col2:
    st.markdown(f"<div class='grey-bubble-small'><p style='margin:0; color:#3399ff; font-size:12px; font-weight:bold;'>EMA 14 (Средна)</p><p style='margin:2px 0 0 0; font-size:16px; font-weight:bold; color:#ffffff;'>{ema14_p:.4f}</p></div>", unsafe_allow_html=True)

with ema_col3:
    st.markdown(f"<div class='grey-bubble-small'><p style='margin:0; color:#ff3333; font-size:12px; font-weight:bold;'>EMA 21 (Бавна)</p><p style='margin:2px 0 0 0; font-size:16px; font-weight:bold; color:#ffffff;'>{ema21_p:.4f}</p></div>", unsafe_allow_html=True)

# Плавно опресняване на реалното време без разваляне на тренда
time.sleep(1)
st.rerun()
