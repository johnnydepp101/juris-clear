import streamlit as st

# 1. КОНФИГУРАЦИЯ И ВАЛЮТЫ
USD_TO_AMD = 400
USD_TO_RUB = 90

# 2. ПОЛНЫЙ СЛОВАРЬ (НИЧЕГО НЕ СОКРАЩАЕМ)
translations = {
    "English": {
        "cur": "$", "rate": 1, "mo": "/ mo",
        "title": "JurisClear AI",
        "subtitle": "Next-Gen Legal Document Audit",
        "one_time": "Single Audit", "pro": "Unlimited Pro",
        "price_9": "9", "price_29": "29",
        "buy": "Get Started", "upload": "Upload PDF contract",
        "demo_tab": "📝 Sample Report", "main_tab": "🚀 Analysis",
        "risk_score_label": "Risk Assessment Score:",
        "risk_desc": "7/10 - High Attention Required",
        "demo_content": """
        **Document Type:** Residential Lease Agreement
        
        🔴 **CRITICAL RISKS FOUND:**
        1. **Clause 4.2 (Rent Increase):** The landlord can increase rent with only 7 days notice. 
           *Advice: Demand at least 30 days notice.*
        2. **Clause 8.1 (Security Deposit):** Deposit is non-refundable under vague 'cleaning' conditions.
           *Advice: Add 'subject to normal wear and tear'.*
           
        ✅ **FINAL VERDICT:** Do not sign without these amendments.
        """,
        "wait_msg": "Please upload a document to begin...",
        "status_ready": "✅ Document analyzed. Results locked.",
        "pay_to_unlock": "🔒 Pay $9 to unlock full risk details."
    },
    "Русский": {
        "cur": "₽", "rate": USD_TO_RUB, "mo": "/ мес.",
        "title": "JurisClear AI",
        "subtitle": "Юридический аудит нового поколения",
        "one_time": "Разовый аудит", "pro": "Безлимит Pro",
        "price_9": str(9 * USD_TO_RUB), "price_29": str(29 * USD_TO_RUB),
        "buy": "Купить доступ", "upload": "Загрузите PDF договор",
        "demo_tab": "📝 Пример отчета", "main_tab": "🚀 Анализ",
        "risk_score_label": "Оценка юридического риска:",
        "risk_desc": "7/10 - Требуется внимание",
        "demo_content": """
        **Тип документа:** Договор аренды жилья
        
        🔴 **КРИТИЧЕСКИЕ РИСКИ:**
        1. **Пункт 4.2 (Повышение цены):** Арендодатель может поднять цену, предупредив всего за 7 дней.
           *Совет: Требуйте срок уведомления не менее 30 дней.*
        2. **Пункт 8.1 (Депозит):** Залог не возвращается при размытых условиях 'уборки'.
           *Совет: Добавьте фразу 'с учетом естественного износа'.*
           
        ✅ **ИТОГ:** Не подписывайте в текущей редакции.
        """,
        "wait_msg": "Загрузите документ для начала...",
        "status_ready": "✅ Документ проанализирован. Результаты скрыты.",
        "pay_to_unlock": "🔒 Оплатите 9$, чтобы открыть полный отчет."
    },
    "Հայերեն": {
        "cur": "֏", "rate": USD_TO_AMD, "mo": "/ ամիս",
        "title": "JurisClear AI",
        "subtitle": "Իրավաբանական աուդիտի նոր սերունդ",
        "one_time": "Մեկանգամյա ստուգում", "pro": "Անսահմանափակ Pro",
        "price_9": str(9 * USD_TO_AMD), "price_29": str(29 * USD_TO_AMD),
        "buy": "Գնել", "upload": "Վերբեռնել PDF պայմանագիրը",
        "demo_tab": "📝 Օրինակ", "main_tab": "🚀 Վերլուծություն",
        "risk_score_label": "Իրավաբանական ռիսկի գնահատականը.",
        "risk_desc": "7/10 - Պահանջվում է ուշադրություն",
        "demo_content": """
        **Փաստաթղթի տեսակը:** Բնակարանի վարձակալության պայմանագիր
        
        🔴 **ԿՐԻՏԻԿԱԿԱՆ ՌԻՍԿԵՐ:**
        1. **Կետ 4.2 (Գնի բարձրացում).** Վարձատուն կարող է բարձրացնել գինը ընդամենը 7 օր առաջ ծանուցելով:
           *Խորհուրդ. Պահանջեք առնվազն 30-օրյա ծանուցում:*
        2. **Կետ 8.1 (Կանխավճար).** Կանխավճարը չի վերադարձվում անորոշ 'մաքրման' պայմանների պատճառով:
           *Խորհուրդ. Ավելացրեք 'բնական մաշվածությունը հաշվի առնելով' արտահայտությունը:*
           
        ✅ **ԵԶՐԱԿԱՑՈՒԹՅՈՒՆ.** Մի ստորագրեք այս տարբերակով:
        """,
        "wait_msg": "Վերբեռնեք փաստաթուղթը սկսելու համար...",
        "status_ready": "✅ Փաստաթուղթը վերլուծված է: Արդյունքները փակ են:",
        "pay_to_unlock": "🔒 Վճարեք $9 ամբողջական հաշվետվությունը բացելու համար:"
    }
}

st.set_page_config(page_title="JurisClear AI", page_icon="⚖️", layout="wide")

# 3. ШАПКА И ЧИСТЫЙ ВЫБОР ЯЗЫКА (БЕЗ КУРСОРA)
st.markdown("<style>div.row-widget.stRadio > div{flex-direction:row; justify-content: flex-end;}</style>", unsafe_allow_html=True)

h_left, h_right = st.columns([3, 1])
with h_left:
    st.markdown(f"# ⚖️ JurisClear AI")
with h_right:
    # Используем radio вместо selectbox, чтобы не было курсора ввода
    lang_choice = st.radio("", ["Русский", "English", "Հայերեն"], label_visibility="collapsed")
    t = translations[lang_choice]

st.markdown(f"#### *{t['subtitle']}*")
st.divider()

# 4. ТАРИФЫ
c1, c2 = st.columns(2)
with c1:
    st.info(f"### {t['one_time']}\n## {t['price_9']} {t['cur']}")
    st.button(t['buy'], key="b9", use_container_width=True)
with c2:
    st.success(f"### {t['pro']}\n## {t['price_29']} {t['cur']} {t['mo']}")
    st.button(t['buy'], key="b29", use_container_width=True)

st.write("")

# 5. РАБОЧАЯ ОБЛАСТЬ
tab1, tab2 = st.tabs([t['main_tab'], t['demo_tab']])

with tab1:
    file = st.file_uploader(t['upload'], type="pdf", key="main_up")
    if file:
        st.subheader(t['risk_score_label'])
        # Визуальная шкала риска (Макет)
        st.error(f"### {t['risk_desc']}")
        st.progress(0.7) # Оценка 7/10
        st.write("---")
        st.info(t['status_ready'])
        st.warning(t['pay_to_unlock'])
    else:
        st.write(t['wait_msg'])

with tab2:
    st.markdown(f"### {t['demo_tab']}")
    st.markdown(t['demo_content'])

st.divider()
st.caption("JurisClear AI © 2026 | Yerevan, Armenia")
