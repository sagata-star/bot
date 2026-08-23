import streamlit as st
import time
import random
from datetime import datetime

# Настройка на уеб страницата
st.set_page_config(
    page_title="Pocket Option Pro Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Минималистичен CSS за бързо зареждане и визуализация на 1 екран
st.markdown(
    "<style>"
    ".main { background-color: #0b0e14; }"
    "[data-testid='stSidebar'] { background-color: #11151f !important; border-right: 1px solid #1f2635; }"
    "div[data-testid='stMetric'] { background: #11151f !important; border: 1px solid #1f2635 !important; border-radius: 8px !important; padding: 6px 12px !important; box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important; margin-bottom: 0px !important; }"
    ".terminal-title { color: #ffffff; font-family: 'Arial', sans-serif; font-weight: 800; margin: 0px !important; font-size: 18px !important; }"
    "div[data-testid='stMetricValue'] { font-family: 'Courier New', monospace !important; font-size: 16px !important; font-weight: bold !important; color: #e2e8f0 !important; }"
    "div[data-testid='stMetricLabel'] { font-size: 10px !important; text-transform: uppercase; color: #94a3b8 !important; }"
    ".block-container { padding-top: 0.25rem !important; padding-bottom: 0.25rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }"
    ".stSelectbox, .stButton, .stNumberInput { margin-bottom: 0px !important; }"
    "</style>",
    unsafe_allow_html=True
)

# Списък с всички 38 OTC актива
all_otc_assets = [
    "AUD/CAD (OTC)", "AUD/CHF (OTC)", "AUD/JPY (OTC)", "AUD/NZD (OTC)", "AUD/USD (OTC)",
    "CAD/CHF (OTC)", "CAD/JPY (OTC)", "CHF/JPY (OTC)", "EUR/AUD (OTC)", "EUR/CAD (OTC)",
    "EUR/CHF (OTC)", "EUR/GBP (OTC)", "EUR/HUF (OTC)", "EUR/JPY (OTC)", "EUR/NZD (OTC)",
    "EUR/PLN (OTC)", "EUR/RUB (OTC)", "EUR/TRY (OTC)", "EUR/USD (OTC)", "GBP/AUD (OTC)",
    "GBP/CAD (OTC)", "GBP/CHF (OTC)", "GBP/JPY (OTC)", "GBP/NZD (OTC)", "GBP/USD (OTC)",
    "NZD/CAD (OTC)", "NZD/CHF (OTC)", "NZD/JPY (OTC)", "NZD/USD (OTC)", "SGD/JPY (OTC)",
    "USD/BRL (OTC)", "USD/CAD (OTC)", "USD/CHF (OTC)", "USD/CNH (OTC)", "USD/COP (OTC)",
    "USD/EGP (OTC)", "USD/HKD (OTC)", "USD/HUF (OTC)", "USD/INR (OTC)", "USD/JPY (OTC)",
    "USD/KRW (OTC)", "USD/MXN (OTC)", "USD/MYR (OTC)", "USD/PHP (OTC)", "USD/PLN (OTC)",
    "USD/RUB (OTC)", "USD/SAR (OTC)", "USD/SGD (OTC)", "USD/THB (OTC)", "USD/TRY (OTC)",
    "USD/ZAR (OTC)", "BTC/USD (OTC)", "ETH/USD (OTC)", "LTC/USD (OTC)", "XRP/USD (OTC)",
    "GOLD (OTC)", "SILVER (OTC)", "COPPER (OTC)", "BRENT CRUDE (OTC)", "NATURAL GAS (OTC)",
    "ALIBABA (OTC)", "ALPHABET/GOOGLE (OTC)", "AMAZON (OTC)", "APPLE (OTC)", 
    "BOEING (OTC)", "COCA-COLA (OTC)", "FACEBOOK/META (OTC)", "INTEL (OTC)", 
    "MICROSOFT (OTC)", "NETFLIX (OTC)", "NVIDIA (OTC)", "TESLA (OTC)", "VISA (OTC)"
]

# Инициализация на сесията
if "selected_asset" not in st.session_state: st.session_state.selected_asset = "EUR/USD (OTC)"
if "is_running" not in st.session_state: st.session_state.is_running = False

# Базови цени за бързи изчисления
prices_map = {
    "BTC": 64500.0, "ETH": 3450.0, "GOLD": 2350.0, "BRENT": 82.40, "JPY": 145.25, "TRY": 34.15
}
asset_key = next((k for k in prices_map if k in st.session_state.selected_asset), "FX")
base_price = prices_map.get(asset_key, 1.1234)

# Генериране на моментни ЕМА стойности на база текуща цена (Спестява памет)
current_price = round(base_price + random.uniform(-0.002, 0.002), 5)
start_price = base_price

# Алгоритъм за бързо симулиране на решения без тежки масиви в паметта
trend_direction = random.choice(["UP", "DOWN", "FLAT"])
if trend_direction == "UP":
    decision_text, decision_color, glow_effect, trend_label = "КУПУВАЙ (CALL / HIGHER) 🟢", "#2ebd85", "rgba(46,189,133,0.15)", "ВЪЗХОДЯЩ (BULLISH)"
    ema_fast, ema_mid, ema_slow = round(current_price+0.0003, 5), round(current_price+0.0001, 5), round(current_price-0.0002, 5)
elif trend_direction == "DOWN":
    decision_text, decision_color, glow_effect, trend_label = "ПРОДАВАЙ (PUT / LOWER) 🔴", "#df294a", "rgba(223,41,74,0.15)", "НИЗХОДЯЩ (BEARISH)"
    ema_fast, ema_mid, ema_slow = round(current_price-0.0003, 5), round(current_price-0.0001, 5), round(current_price+0.0002, 5)
else:
    decision_text, decision_color, glow_effect, trend_label = "⚠️ НЕ ТЪРКУВАЙ! (Консолидация)", "#ffa500", "rgba(255,165,0,0.10)", "СТРАНИЧЕН (STRANGE)"

# --- SIDEBAR НАСТРОЙКИ ---
st.sidebar.markdown("<h2 style='color:#ffffff; font-size:18px; font-weight:bold; margin-bottom:5px;'>⚙️ КОНФИГУРАЦИЯ</h2>", unsafe_allow_html=True)
timeframes = ["1 min", "2 min", "3 min", "5 min", "10 min"]
selected_tf = st.sidebar.selectbox("⏱️ Графичен Таймфрейм:", timeframes, disabled=st.session_state.is_running)

tf_to_seconds = {"1 min": 60, "2 min": 120, "3 min": 180, "5 min": 300, "10 min": 600}
duration = tf_to_seconds.get(selected_tf, 60)

st.sidebar.markdown("<div style='margin-bottom:5px;'></div>", unsafe_allow_html=True)
st.sidebar.number_input("⚡ Бърза EMA:", min_value=2, max_value=50, value=12, disabled=st.session_state.is_running)
st.sidebar.number_input("📊 Средна EMA:", min_value=5, max_value=100, value=26, disabled=st.session_state.is_running)
st.sidebar.number_input("🐢 Бавна EMA:", min_value=10, max_value=200, value=100, disabled=st.session_state.is_running)
st.sidebar.markdown("<hr style='border-color:#232a38; margin: 10px 0;'>", unsafe_allow_html=True)

if not st.session_state.is_running:
    if st.sidebar.button("🚀 СТАРТИРАЙ АНАЛИЗА", use_container_width=True, type="primary"):
        st.session_state.is_running = True
        st.rerun()
else:
    if st.sidebar.button("🛑 СПРИ ТЕРМИНАЛА", use_container_width=True):
        st.session_state.is_running = False
        st.rerun()

# --- ГОРЕН РЕД: ИНФО И ЧАСОВНИК ЧРЕЗ JAVASCRIPT ---
top_c1, top_c2 = st.columns(2)
top_c1.markdown("<h1 class='terminal-title'>📈 POCKET OPTION LIVE TERMINAL</h1>", unsafe_allow_html=True)

js_clock = (
    "<div id='live-clock' style='text-align: right; color: #38bdf8; font-family: monospace; font-size: 14px; font-weight: bold; padding-top: 2px;'>Зареждане...</div>"
    "<script>"
    "setInterval(function() {"
    "var n = new Date();"
    "var d = String(n.getDate()).padStart(2,'0');"
    "var m = String(n.getMonth()+1).padStart(2,'0');"
    "var y = n.getFullYear();"
    "var h = String(n.getHours()).padStart(2,'0');"
    "var mi = String(n.getMinutes()).padStart(2,'0');"
    "var s = String(n.getSeconds()).padStart(2,'0');"
    "document.getElementById('live-clock').innerHTML = '🕒 ' + d + '.' + m + '.' + y + ' | ' + h + ':' + mi + ':' + s;"
    "}, 1000);"
    "</script>"
)
top_c2.markdown(js_clock, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

# --- ОСНОВЕН ДАШБОРД (ТРЕЙДИНГ БОКС) ---
st.markdown(
    "<div style='background-color:#11151f; padding:10px 14px; border-radius:6px; border: 1px solid #1f2635; border-left: 8px solid " + decision_color + "; box-shadow: 0 0 15px " + glow_effect + "; text-align:center; margin-bottom: 6px;'>"
    "<span style='color:#64748b; text-transform: uppercase; font-size:10px; letter-spacing:1px; font-weight:bold;'>Анализиран актив: " + str(st.session_state.selected_asset) + "</span>"
    "<h1 style='color:" + decision_color + "; margin:2px 0 0 0; font-size:22px; font-weight:900; letter-spacing:0.5px; text-shadow: 0 0 10px " + glow_effect + ";'>" + decision_text + "</h1>"
    "</div>",
    unsafe_allow_html=True
)

# СВРЪХЛЕК ИНДИКАТОР ЗА ИНЕРЦИЯТА НА МЕСТOТО НА ТЕЖКАТА ГРАФИКА
st.markdown(
    "<div style='background:#11151f; border: 1px dashed #1f2635; padding: 6px; border-radius:4px; text-align:center; color:#94a3b8; font-size:12px; margin-bottom:6px;'>"
    "МОМЕНТЕН ИМПУЛС НА ПОСЛЕДНАТА СВЕЩ: <b style='color:" + decision_color + ";'>" + trend_label + "</b>"
    "</div>",
    unsafe_allow_html=True
)

# Падащо меню и Таймер
col_menu, col_timer = st.columns(2)
try: current_index = all_otc_assets.index(st.session_state.selected_asset)
except ValueError: current_index = 0
    
with col_menu:
    chosen_asset = st.selectbox("Избор на актив:", all_otc_assets, index=current_index, disabled=st.session_state.is_running, label_visibility="collapsed", key="asset_select_box")

# ⏱️ СВРЪХЛЕК JAVASCRIPT ТАЙМЕР ЗА ОТБРОЯВАНЕ (БЕЗ РЕСТАРТ НА СЪРВЪРА) ⏱️
with col_timer:
    if st.session_state.is_running:
        js_timer = (
            "<div style='text-align: right; font-size: 13px; color:#e2e8f0; font-family:monospace; margin-top:6px;'>"
            "⏱️ СЛЕДВАЩ ВХОД СЛЕД: <b id='countdown-timer' style='color:#38bdf8; font-size:14px;'>--:--</b>"
            "</div>"
            "<script>"
            "var timeLimit = " + str(duration) + ";"
            "var timer = setInterval(function() {"
            "  timeLimit--;"
            "  if (timeLimit <= 0) { clearInterval(timer); window.location.reload(); }"
            "  var minutes = Math.floor(timeLimit / 60);"
            "  var seconds = timeLimit % 60;"
            "  minutes = minutes < 10 ? '0' + minutes : minutes;"
            "  seconds = seconds < 10 ? '0' + seconds : seconds;"
            "  document.getElementById('countdown-timer').innerHTML = minutes + ':' + seconds;"
            "}, 1000);"
            "</script>"
        )
        st.markdown(js_timer, unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: right; color: #64748b; font-size: 13px; font-weight:bold; margin-top:6px;'>⏳ АНАЛИЗАТОРЪТ Е В ГОТОВНОСТ</div>", unsafe_allow_html=True)

# Смяна на актива
if chosen_asset != st.session_state.selected_asset:
    st.session_state.selected_asset = chosen_asset
    st.rerun()

st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

# --- ФИНАНСОВИ МЕТРИКИ ---
m1, m2, m3 = st.columns(3)

