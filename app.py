import streamlit as st
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
    .direction-arrow { font-size: 70px !important; font-weight: bold; text-align: center; line-height: 1; }
    .direction-text { font-size: 28px !important; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 3. Списък с активи
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
    "GBP/CAD (OTC)", "EUR/AUD (OTC)", "AUD/NZD (OTC)", "GOLD (OTC)", "SILVER (OTC)"
]

# 4. Функция за генериране на базова история
def generate_fresh_history(asset_name, tf_seconds):
    if "JPY" in asset_name: base_price = 145.25
    elif "CHF" in asset_name: base_price = 0.8950
    elif "GOLD" in asset_name: base_price = 2350.00
    elif "SILVER" in asset_name: base_price = 28.50
    elif "BTC" in asset_name: base_price = 64500.00
    elif "ETH" in asset_name: base_price = 3450.00
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

# 5. Страничен панел и настройки
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

# Динамични EMA периоди и прагове за волатилност
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
st.sidebar.markdown("**Активни ЕМА периоди:**")
st.sidebar.text(f"Бърза: EMA {p_fast}")
st.sidebar.text(f"Средна: EMA {p_mid}")
st.sidebar.text(f"Бавна: EMA {p_slow}")

# Инициализиране на сесията при смяна на актив или таймфрейм
if "current_asset" not in st.session_state or st.session_state.current_asset != selected_asset or "current_tf" not in st.session_state or st.session_state.current_tf != tf_seconds:
    st.session_state.current_asset = selected_asset
    st.session_state.current_tf = tf_seconds
    st.session_state.df_history = generate_fresh_history(selected_asset, tf_seconds)
    st.session_state.last_bucket = int(datetime.now().timestamp() / tf_seconds)

# 6. Оптимизиран фрагмент за реално време (Опреснява само графики/данни на всеки 1 секунда без лаг)
@st.fragment(run_every=1.0)
def update_dashboard():
    now = datetime.now()
    current_bucket = int(now.timestamp() / tf_seconds)
    remaining_seconds = tf_seconds - (int(now.timestamp()) % tf_seconds)
    
    # Добавяне на нова свещ при изтичане на времевия диапазон
    if current_bucket != st.session_state.last_bucket:
        st.session_state.last_bucket = current_bucket
        last_price = st.session_state.df_history["Price"].iloc[-1]
        new_price = last_price + random.uniform(-last_price * 0.0003, last_price * 0.0003)
        new_row = pd.DataFrame({"Timestamp": [now], "Price": [new_price]})
        st.session_state.df_history = pd.concat([st.session_state.df_history.iloc[1:], new_row], ignore_index=True)
    else:
        # Симулиране на тикови движения в рамките на текущата свещ
        last_price = st.session_state.df_history["Price"].iloc[-1]
        st.session_state.df_history.loc[st.session_state.df_history.index[-1], "Price"] = last_price + random.uniform(-last_price * 0.0001, last_price * 0.0001)

    df = st.session_state.df_history.copy()
    
    # Изчисляване на индикатори
    df['EMA_FAST'] = df['Price'].ewm(span=p_fast, adjust=False).mean()
    df['EMA_MID'] = df['Price'].ewm(span=p_mid, adjust=False).mean()
    df['EMA_SLOW'] = df['Price'].ewm(span=p_slow, adjust=False).mean()

    current_p = df['Price'].iloc[-1]
    ema_fast_p = df['EMA_FAST'].iloc[-1]
    ema_mid_p = df['EMA_MID'].iloc[-1]
    ema_slow_p = df['EMA_SLOW'].iloc[-1]

    ema_spread_pct = (abs(ema_fast_p - ema_slow_p) / ema_slow_p) * 100
    is_low_volatility = ema_spread_pct < volatility_threshold

    # Горна секция с метрики
    t_col1, t_col2, t_col3 = st.columns(3)
    t_col1.metric("🕒 Текущо време", now.strftime("%H:%M:%S"))
    t_col2.metric(f"⏳ Следващ вход ({timeframe_label})", f"{remaining_seconds} сек.")
    
    fmt_str = "{:.6f}" if current_p < 0.01 else ("{:.4f}" if current_p < 1000 else "{:.2f}")
    t_col3.metric(f"Цена {selected_asset}", fmt_str.format(current_p))

    st.write("---")

    # Логика за сигнали
    if is_low_volatility:
        buy_ratio, sell_ratio = random.randint(49, 51), random.randint(49, 51)
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠➡</div><div class='direction-text' style='color: #ffaa00;'>LOW VOLATILITY</div>"
        signal_type = "warning"
        status_text = f"❌ НИСКА ВОЛАТИЛНОСТ / ОПАСЕН ВХОД: Линиите са слепени (Разстояние: {ema_spread_pct:.4f}%). Изчакайте!"
    elif ema_fast_p > ema_mid_p > ema_slow_p:
        if current_p >= ema_fast_p:
            buy_ratio = random.randint(85, 96)
            sell_ratio = 100 - buy_ratio
            arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
            signal_type = "success"
            status_text = f"🔥 СИЛЕН ИМПУЛС: Потвърден възходящ тренд на {timeframe_label}."
        else:
            buy_ratio = random.randint(60, 70)
            sell_ratio = 100 - buy_ratio
            arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬆</div><div class='direction-text' style='color: #ffaa00;'>WEAK BUY</div>"
            signal_type = "warning"
            status_text = f"⏳ КОРЕКЦИЯ: Възходящ тренд, но цената падна под ЕМА {p_fast}."
    elif ema_fast_p < ema_mid_p < ema_slow_p:
        if current_p <= ema_fast_p:
            sell_ratio = random.randint(85, 96)
            buy_ratio = 100 - sell_ratio
            arrow_html = "<div class='direction-arrow' style='color: #ff3333;'>⬇</div><div class='direction-text' style='color: #ff3333;'>STRONG SELL</div>"
            signal_type = "error"
            status_text = f"🚨 СИЛЕН ИМПУЛС: Потвърден низходящ тренд на {timeframe_label}."
        else:
            sell_ratio = random.randint(60, 70)
            buy_ratio = 100 - sell_ratio
            arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬇</div><div class='direction-text' style='color: #ffaa00;'>WEAK SELL</div>"
            signal_type = "warning"
            status_text = f"⏳ КОРЕКЦИЯ: Низходящ тренд, но цената излезе над ЕМА {p_fast}."
    else:
        buy_ratio, sell_ratio = random.randint(47, 53), random.randint(47, 53)
        arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡</div><div class='direction-text' style='color: #aaaaaa;'>NO SIGNAL</div>"
        signal_type = "info"
        status_text = f"📉 КОНСОЛИДАЦИЯ (ФЛАТ): Няма ясна трендова посока."

    # Рендиране на среден панел
    sig_col1, sig_col2 = st.columns(2)
    with sig_col1:
        st.markdown(arrow_html, unsafe_allow_html=True)
    with sig_col2:
        st.subheader(f"📊 Пазарно съотношение ({timeframe_label})")
        st.markdown(f"**Купувачи:** {buy_ratio}% | **Продавачи:** {sell_ratio}%")
        st.progress(buy_ratio / 100)
        if signal_type == "success": st.success(status_text)
        elif signal_type == "warning": st.warning(status_text)
        elif signal_type == "error": st.error(status_text)
        else: st.info(status_text)

    # Долен панел с индикатори
    st.write("---")
    st.markdown(f"##### 📊 Технически показатели за {selected_asset} {ema_label_suffix}")
    
    ema_col1, ema_col2, ema_col3 = st.columns(3)
    ema_col1.metric(label=f"EMA {p_fast} (Бърза)", value=fmt_str.format(ema_fast_p))
    ema_col2.metric(label=f"EMA {p_mid} (Средна)", value=fmt_str.format(ema_mid_p))
    ema_col3.metric(label=f"EMA {p_slow} (Бавна)", value=fmt_str.format(ema_slow_p))
    
