import streamlit as st

# 1. КОНФИГУРАЦИЯ И КУРСЫ ВАЛЮТ
USD_TO_AMD = 400
USD_TO_RUB = 90

# 2. УЛУЧШЕННЫЙ СЛОВАРЬ (С учетом твоих правок)
translations = {
    "English": {
        "cur": "$", "rate": 1, "mo": "/ mo",
        "title": "JurisClear AI",
        "subtitle": "Next-Gen Legal Document Audit",
        "one_time": "Single Audit", "pro": "Unlimited Pro",
        "price_9": "9", "price_29": "29",
        "buy": "Get Started", "upload": "Upload PDF contract",
        "demo_tab": "📝 Sample Report", "main_tab": "🚀 Analysis",
        "demo_content": "🔴 **Critical Risk:** Clause 4.2 allows price increases without notice.",
        "risk_wait": "Waiting for document...",
        "status_ok": "✅ File ready for audit",
    },
    "Русский": {
        "cur": "₽", "rate": USD_TO_RUB, "mo": "/ мес.",
        "title": "JurisClear AI",
        "subtitle": "Юридический аудит нового поколения",
        "one_time": "Разовый аудит", "pro": "Безлимит Pro",
        "price_9": str(9 * USD_TO_RUB), "price_29": str(29 * USD_TO_RUB),
        "buy": "Купить доступ", "upload": "Загрузите PDF договор",
        "demo_tab": "📝 Пример отчета", "main_tab": "🚀 Анализ",
        "demo_content": "🔴 **Критический риск:** Пункт 4.2 позволяет повышать цену без уведомления.",
        "risk_wait": "Ожидание документа...",
        "status_ok": "✅ Файл готов к проверке",
    },
    "Հայերեն": {
        "cur": "֏", "rate": USD_TO_AMD, "mo": "/ ամիս",
        "title": "JurisClear AI",
        "subtitle": "Իրավաբանական աուդիտի նոր սերունդ",
        "one_time": "Մեկանգամյա ստուգում", "pro": "Անսահմանափակ Pro",
        "price_9": str(9 * USD_TO_AMD), "price_29": str(29 * USD_TO_AMD),
        "buy": "Գնել", "upload": "Վերբեռնել PDF պայմանագիրը",
        "demo_tab": "📝 Օրինակ", "main_tab": "🚀 Վերլուծություն",
        "demo_content": "🔴 **Կրիտիկական ռիսկ:** 4.2 կետը թույլ է տալիս բարձրացնել գինը առանց ծանուցման:",
        "risk_wait": "Սպասում ենք փաստաթղթին...",
        "status_ok": "✅ Ֆայլը պատրաստ է ստուգման",
    }
}

st.set_page_config(page_title="JurisClear AI", page_icon="⚖️", layout="wide")

# 3. ВЕРХНЯЯ ПАНЕЛЬ (Язык теперь в углу)
head_left, head_right = st.columns([4, 1])

with head_right:
    # Убираем лишние отступы для выбора языка
    lang_choice = st.selectbox("", ["Русский", "English", "Հայերեն"], label_visibility="collapsed")
    t = translations[lang_choice]

with head_left:
    st.markdown(f"# ⚖️ {t['title']}")
    st.markdown(f"*{t['subtitle']}*")

st.divider()

# 4. ТАРИФНЫЕ КАРТОЧКИ
col1, col2 = st.columns(2)

with col1:
    st.info(f"### {t['one_time']}\n## {t['price_9']} {t['cur']}")
    st.button(t['buy'], key="btn9", use_container_width=True)

with col2:
    # ЗДЕСЬ ИСПРАВЛЕНА НАДПИСЬ / MO
    st.success(f"### {t['pro']}\n## {t['price_29']} {t['cur']} {t['mo']}")
    st.button(t['buy'], key="btn29", use_container_width=True)

st.write("")

# 5. РАБОЧАЯ ОБЛАСТЬ (Упрощена для мобильных)
tab_main, tab_demo = st.tabs([t['main_tab'], t['demo_tab']])

with tab_main:
    # Ключ для file_uploader добавлен для стабильности сессии
    uploaded_file = st.file_uploader(t['upload'], type="pdf", key="legal_file_uploader")
    
    if uploaded_file is not None:
        st.success(t['status_ok'])
        st.warning("🔒 Payment required to unlock full AI analysis.")
    else:
        st.write(f"ℹ️ {t['risk_wait']}")

with tab_demo:
    st.markdown(f"### {t['demo_tab']}")
    st.write(t['demo_content'])

st.divider()
st.caption("JurisClear AI © 2026 | Yerevan, Armenia")
