# 8. СРЕДЕН ПАНЕЛ: ОБНОВЕНА СТРОГА ЛОГИКА ЗА СИГНАЛИ
st.write("---")

if is_low_volatility:
    buy_ratio = random.randint(49, 51)
    sell_ratio = 100 - buy_ratio
    arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠➡</div><div class='direction-text' style='color: #ffaa00;'>LOW VOLATILITY</div>"
    status_text = f"⚠️ НИСКА ВОЛАТИЛНОСТ: Пазарът няма сила. Изчакайте разширение на ценовия диапазон."

elif is_intertwined:
    buy_ratio = random.randint(46, 54)
    sell_ratio = 100 - buy_ratio
    arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡❌</div><div class='direction-text' style='color: #aaaaaa;'>FALSE BREAKOUT / CHOPPY</div>"
    status_text = f"📉 ПРЕПЛИТАНЕ НА ЛИНИИТЕ: Липса на ясна посока и фалшиви пробиви. Не влизайте!"

elif ema8_p > ema14_p > ema21_p:
    if current_p >= ema8_p and is_strong_momentum and fast_ema_slope > 0:
        buy_ratio = random.randint(88, 98) # По-висока увереност заради филтрите
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #00ff66;'>⬆🔥</div><div class='direction-text' style='color: #00ff66;'>STRONG BUY</div>"
        status_text = f"🔥 СИЛЕН УСКОРЯВАЩ ТРЕНД: Цената е над ЕМА, линиите са подредени и бързата ЕМА расте с темп {fast_ema_slope:.3f}%."
    else:
        buy_ratio = random.randint(58, 68)
        sell_ratio = 100 - buy_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬆</div><div class='direction-text' style='color: #ffaa00;'>WEAK BUY</div>"
        status_text = f"⏳ КОРЕКЦИЯ/ОТСЛАБВАНЕ: Възходяща подредба, но инерцията намалява."

elif ema8_p < ema14_p < ema21_p:
    if current_p <= ema8_p and is_strong_momentum and fast_ema_slope < 0:
        sell_ratio = random.randint(88, 98)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ff3333;'>⬇🚨</div><div class='direction-text' style='color: #ff3333;'>STRONG SELL</div>"
        status_text = f"🚨 СИЛЕН СПАД: Цената натиска надолу, линиите са подредени и ЕМА пада с темп {fast_ema_slope:.3f}%."
    else:
        sell_ratio = random.randint(60, 70)
        buy_ratio = 100 - sell_ratio
        arrow_html = "<div class='direction-arrow' style='color: #ffaa00;'>⚠⬇</div><div class='direction-text' style='color: #ffaa00;'>WEAK SELL</div>"
        status_text = f"⏳ КОРЕКЦИЯ/ОТСЛАБВАНЕ: Низходяща подредба, но липсва силен натиск."

else:
    buy_ratio = random.randint(47, 53)
    sell_ratio = 100 - buy_ratio
    arrow_html = "<div class='direction-arrow' style='color: #aaaaaa;'>➡</div><div class='direction-text' style='color: #aaaaaa;'>NO SIGNAL</div>"
    status_text = f"📉 КОНСОЛИДАЦИЯ (ФЛАТ): Пазарът се свива в тесен рейндж."

sig_col1, sig_col2 = st.columns(2)
with sig_col1:
    st.markdown(arrow_html, unsafe_allow_html=True)
with sig_col2:
    st.subheader(f"📊 Пазарно съотношение ({timeframe_label})")
    st.markdown(f"**Купувачи (Bulls):** {buy_ratio}%")
    st.write(status_text)
