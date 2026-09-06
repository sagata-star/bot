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

# 2. Инжектиране на компактни CSS стилове (Оптимизирани за пълна визуализация без скрол)
st.markdown("""
    <style>
    .main { background-color: #1c1f26; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0px !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 4px !important; }
    div[data-testid="stMetricValue"] { font-size: 16px !important; font-weight: bold; line-height: 1.1 !important; }
    div[data-testid="stMetricLabel"] { font-size: 11px !important; margin-bottom: 0px !important; }
    
    /* Стил за заглавията и разделителите */
    h1 { font-size: 18px !important; margin-top: 0px !important; margin-bottom: 2px !important; padding: 0px !important; }
    h3 { font-size: 13px !important; margin-top: 0px !important; margin-bottom: 2px !important; }
    h5 { font-size: 12px !important; margin-top: 2px !important; margin-bottom: 2px !important; }
    
    /* Стил за голямата цветна стрелка и текст */
    .direction-arrow { font-size: 40px !important; font-weight: bold; text-align: center; line-height: 1; margin: 0px !important; }
    .direction-text { font-size: 18px !important; font-weight: bold; text-align: center; margin: 0px !important; }
    .compact-hr { margin-top: 3px !important; margin-bottom: 3px !important; border: 0; border-top: 1px solid #333; }
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

# 4. Функция за генериране на базова история
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
    # ПОПРАВКА: Генерираме 350 свещи дълбочина, за да може EMA 50 да се изчисли безопасно без математически срив
    current_time = datetime.now() - timedelta(seconds=350 * tf_seconds)
    current_price = base_price
    
    for i in range(350):
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

# --- ИЗИCКВАНЕ 1: АДАПТИВНИ ЕМА ПЕРИОДИ И ПРАГОВЕ ЗА ВОЛАТИЛНОСТ ---
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

# 6. СИНХРОНИЗАЦИЯ И СТАБИЛИЗАЦИЯ НА ДАННИТЕ
if "current_asset" not in st.session_state or st.session_state.current_asset != selected_asset or "current_tf" not in st.session_state or st.session_state.current_tf != tf_seconds:
    st.session_state.current_asset = selected_asset
    st.session_state.current_tf = tf_seconds
    st.session_state.df_history = generate_fresh_history(selected_asset, tf_seconds)
    st.session_state.last_update_timestamp = int(time.time() / tf_seconds)

# Изчисляване на времевата рамка в реално време
now = datetime.now()
current_timestamp_bucket = int(time.time() / tf_seconds)
remaining_seconds = tf_seconds - (int(time.time()) % tf_seconds)

# Логика при настъпване на нова свещ
if current_timestamp_bucket != st.session_state.last_update_timestamp:
    st.session_state.last_update_timestamp = current_timestamp_bucket
    last_price = st.session_state.df_history["Price"].iloc[-1]
    new_price = last_price + random.uniform(-last_price * 0.0005, last_price * 0.0005)
    new_row = pd.DataFrame({"Timestamp": [now], "Price": [new_price]})
    st.session_state.df_history = pd.concat([st.session_state.df_history.iloc[1:], new_row], ignore_index=True)

df = st.session_state.df_history.copy()

# СОФТУЕРНА ЗАЩИТА: Изчисляване на индикаторите с подсигурен минимум (`min_periods=1`) против замръзване
df['EMA_8'] = df['Price'].ewm(span=p_fast, min_periods=1, adjust=False).mean()
df['EMA_14'] = df['Price'].ewm(span=p_mid, min_periods=1, adjust=False).mean()
df['EMA_21'] = df['Price'].ewm(span=p_slow, min_periods=1, adjust=False).mean()

current_time_str = now.strftime("%H:%M:%S")
current_p = df['Price'].iloc[-1]
ema8_p = df['EMA_8'].iloc[-1]
ema14_p = df['EMA_14'].iloc[-1]
ema21_p = df['EMA_21'].iloc[-1]

# --- ИЗИCКВАНЕ 2: ИНДИКАТОР ЗА ВОЛАТИЛНОСТ (Процентно разстояние между бърза и бавна линия)
ema_spread_pct = (abs(ema8_p - ema21_p) / ema21_p) * 100
is_low_volatility = ema_spread_pct < volatility_threshold

# --- МАТЕМАТИЧЕСКА СИСТЕМА ЗА ИЗЧИСЛЯВАНЕ НА ДОСТОВЕРНОСТТА НА СИГНАЛА ---
if is_low_volatility:
    signal_accuracy = random.randint(8, 18)
    status_label = "🚫 КРИТИЧНО НИСКА"
elif ema8_p > ema14_p > ema21_p:
    base_acc = 72.0
    spread_bonus = min(16.0, (ema_spread_pct / volatility_threshold) * 4)
    price_bonus = 10.0 if current_p >= ema8_p else -8.0
    signal_accuracy = round(base_acc + spread_bonus + price_bonus, 1)
    status_label = "💎 ВИСОКА ТОЧНОСТ" if signal_accuracy >= 85 else "✅ СТАБИЛЕН СИГНАЛ"
elif ema8_p < ema14_p < ema21_p:
    base_acc = 72.0
    spread_bonus = min(16.0, (ema_spread_pct / volatility_threshold) * 4)
    price_bonus = 10.0 if current_p <= ema8_p else -8.0
    signal_accuracy = round(base_acc + spread_bonus + price_bonus, 1)
    status_label = "💎 ВИСОКА ТОЧНОСТ" if signal_accuracy >= 85 else "✅ СТАБИЛЕН СИГНАЛ"
else:
    signal_accuracy = random.randint(38, 49)
    status_label = "⚠️ СРЕДНА/ФЛАТ"

signal_accuracy = max(0.0, min(99.0, signal_accuracy))

# 7. ГОРЕН ПАНЕЛ: ЧАСОВНИК, ТАЙМЕР И ЦЕНА
t_col1, t_col2, t_col3 = st.columns(3)
t_col1.metric("🕒 Време на затваряне", current_time_str)
t_col2.metric(f"⏳ Опресняване след ({timeframe_label})", f"{remaining_seconds} сек.")

if current_p < 0.01: fmt_str = "{:.6f}"
elif current_p < 1000: fmt_str = "{:.4f}"
else: fmt_str = "{:.2f}"

t_col3.metric(f"Цена {selected_asset}", fmt_str.format(current_p))

# Елиминиране на дебелия разделител в полза на супер компактна HTML линия
st.markdown("<hr class='compact-hr'>", unsafe_allow_html=True)

# 8. СРЕДЕН ПАНЕЛ: СТРОГА ЛОГИКА ЗА СИГНАЛИ СПРЯМО СЕКУНДНИЯ/МИНУТНИЯ ТАЙМФРЕЙМ
if is_low_volatility:
    buy_ratio = random.randint(49, 51)  # Автоматично занижаване на пазарното съотношение при липса на волатилност
    sell_ratio = 100 - buy_ratio
    arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠➡</div><div class='direction-text' style='color: #ffaa00;'>LOW VOLATILITY</div>"
    signal_func = st.warning
    status_text = f"⚠️ НИСКА ВОЛАТИЛНОСТ / ОПАСЕН ВХОД: Линиите са слепени под прага от {volatility_threshold}%."

elif ema8_p > ema14_p > ema21_p:
    if current_p >= ema8_p:
        buy_ratio = random.randint(85, 96)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
        signal_func = st.success
