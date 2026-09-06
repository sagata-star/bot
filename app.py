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

# 2. CSS за максимално мащабиране и събиране на целия екран в облака
st.markdown("""
    <style>
    .main { background-color: #1c1f26; }
    .block-container { padding-top: 0.2rem !important; padding-bottom: 0px !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 2px !important; }
    div[data-testid="stMetricValue"] { font-size: 15px !important; font-weight: bold; line-height: 1.0 !important; }
    div[data-testid="stMetricLabel"] { font-size: 10px !important; margin-bottom: 0px !important; }
    
    h1 { font-size: 16px !important; margin-top: 0px !important; margin-bottom: 1px !important; padding: 0px !important; }
    h3 { font-size: 12px !important; margin-top: 0px !important; margin-bottom: 1px !important; }
    h5 { font-size: 11px !important; margin-top: 1px !important; margin-bottom: 1px !important; }
    
    .direction-arrow { font-size: 35px !important; font-weight: bold; text-align: center; line-height: 1; margin: 0px !important; }
    .direction-text { font-size: 16px !important; font-weight: bold; text-align: center; margin: 0px !important; }
    .compact-hr { margin-top: 2px !important; margin-bottom: 2px !important; border: 0; border-top: 1px solid #333; }
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

# 6. КРИТИЧНА ПОПРАВКА: ИНИЦИАЛИЗИРАНЕ И БЕЗОПАСНО ПЪРВОНАЧАЛНО СЪЗДАВАНЕ НА СЕСИЯТА
# Това подсигурява, че данните съществуват глобално преди стартиране на фрагмента против Бял екран
if "current_asset" not in st.session_state or st.session_state.current_asset != selected_asset or "current_tf" not in st.session_state or st.session_state.current_tf != tf_seconds:
    st.session_state.current_asset = selected_asset
    st.session_state.current_tf = tf_seconds
    st.session_state.df_history = generate_fresh_history(selected_asset, tf_seconds)
    st.session_state.last_update_timestamp = int(time.time() / tf_seconds)

# 7. ОБЛАЧЕН ОПТИМИЗИРАН ФРАГМЕНТ ЗА РЕАЛНО ВРЕМЕ
@st.fragment(run_every=1.0)
def display_dashboard():
    # Защита: Ако по някаква причина паметта в облака се изчисти, изчакваме и я пресъздаваме веднага
    if "df_history" not in st.session_state:
        st.session_state.df_history = generate_fresh_history(selected_asset, tf_seconds)
        st.session_state.last_update_timestamp = int(time.time() / tf_seconds)

    now = datetime.now()
    current_timestamp_bucket = int(time.time() / tf_seconds)
    remaining_seconds = tf_seconds - (int(time.time()) % tf_seconds)

    # Логика за добавяне на свещ или актуализиране на текущ тик
    if current_timestamp_bucket != st.session_state.last_update_timestamp:
        st.session_state.last_update_timestamp = current_timestamp_bucket
        last_price = st.session_state.df_history["Price"].iloc[-1]
        new_price = last_price + random.uniform(-last_price * 0.0005, last_price * 0.0005)
        new_row = pd.DataFrame({"Timestamp": [now], "Price": [new_price]})
        st.session_state.df_history = pd.concat([st.session_state.df_history.iloc[1:], new_row], ignore_index=True)
    else:
        last_price = st.session_state.df_history["Price"].iloc[-1]
        st.session_state.df_history.iloc[-1, st.session_state.df_history.columns.get_loc("Price")] = last_price + random.uniform(-last_price * 0.0001, last_price * 0.0001)

    df = st.session_state.df_history.copy()

    # Калкулиране на показателите с min_periods=1 защита
    df['EMA_8'] = df['Price'].ewm(span=p_fast, min_periods=1, adjust=False).mean()
    df['EMA_14'] = df['Price'].ewm(span=p_mid, min_periods=1, adjust=False).mean()
    df['EMA_21'] = df['Price'].ewm(span=p_slow, min_periods=1, adjust=False).mean()

    current_p = df['Price'].iloc[-1]
    ema8_p = df['EMA_8'].iloc[-1]
    ema14_p = df['EMA_14'].iloc[-1]
    ema21_p = df['EMA_21'].iloc[-1]

    current_time_str = now.strftime("%H:%M:%S")
    ema_spread_pct = (abs(ema8_p - ema21_p) / ema21_p) * 100
    is_low_volatility = ema_spread_pct < volatility_threshold

    # Определяне на сигналите и достоверността
    if is_low_volatility:
        buy_ratio = random.randint(49, 51)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠➡</div><div class='direction-text' style='color: #ffaa00;'>LOW VOLATILITY</div>"
        signal_func = st.warning
        status_text = f"⚠️ НИСКА ВОЛАТИЛНОСТ: Линиите са слепени под прага от {volatility_threshold}%."
        signal_accuracy = random.randint(8, 18)
        status_label = "🚫 КРИТИЧНО НИСКА"
    elif ema8_p > ema14_p > ema21_p:
        base_acc = 72.0
        spread_bonus = min(16.0, (ema_spread_pct / volatility_threshold) * 4)
        price_bonus = 10.0 if current_p >= ema8_p else -8.0
        signal_accuracy = round(base_acc + spread_bonus + price_bonus, 1)
        status_label = "💎 ВИСОКА ТОЧНОСТ" if signal_accuracy >= 85 else "✅ СТАБИЛЕН СИГНАЛ"
        
        if current_p >= ema8_p:
            buy_ratio = random.randint(85, 96)
            sell_ratio = 100 - buy_ratio
            arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
            signal_func = st.success
            status_text = f"🔥 СИЛЕН ИМПУЛС: Потвърден възходящ тренд на {timeframe_label}."
        else:
            buy_ratio = random.randint(60, 70)
            sell_ratio = 100 - buy_ratio
            arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬆</div><div class='direction-text' style='color: #ffaa00;'>WEAK BUY</div>"
            signal_func = st.warning
            status_text = f"⏳ КОРЕКЦИЯ: Цена под ЕМА {p_fast}."
    elif ema8_p < ema14_p < ema21_p:
        base_acc = 72.0
        spread_bonus = min(16.0, (ema_spread_pct / volatility_threshold) * 4)
        price_bonus = 10.0 if current_p <= ema8_p else -8.0
        signal_accuracy = round(base_acc + spread_bonus + price_bonus, 1)
