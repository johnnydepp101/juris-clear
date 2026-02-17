import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

# --- 1. КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="JurisClear AI", page_icon="⚖️", layout="wide")

# --- 2. CSS ДЛЯ ЧИСТОГО ИНТЕРФЕЙСА ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    .stButton>button {width: 100%; border-radius: 10px; height: 3em; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ИНИЦИАЛИЗАЦИЯ API ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 4. ПЕРЕВОДЫ И ВАЛЮТЫ ---
translations = {
    "English": {
        "cur": "$", "p9": "9", "p29": "29", "mo": "/mo",
        "title": "Professional Legal Audit",
        "one_time": "Single Audit", "pro": "Unlimited Pro",
        "buy": "Buy Access", "upload": "Upload PDF Contract",
        "btn_run": "Start AI Analysis", "demo_tab": "📝 Sample Report",
        "main_tab": "🚀 Analysis", "wait": "Please upload a file...",
        "pay_msg": "🔒 Pay {p} {c} to unlock full report.",
        "risk_label": "Legal Assessment:",
        "demo_txt": "🔴 **Risk:** Clause 4.2 allows price increases.\n✅ **Verdict:** High Risk."
    },
    "Русский": {
        "cur": "$", "p9": "9", "p29": "29", "mo": "/мес.",
        "title": "Профессиональный юридический аудит",
        "one_time": "Разовый аудит", "pro": "Безлимит Pro",
        "buy": "Купить доступ", "upload": "Загрузите PDF договор",
        "btn_run": "Начать ИИ анализ", "demo_tab": "📝 Пример отчета",
        "main_tab": "🚀 Анализ", "wait": "Загрузите файл для начала...",
        "pay_msg": "🔒 Оплатите {p} {c}, чтобы открыть полный отчет.",
        "risk_label": "Юридическая оценка:",
        "demo_txt": "🔴 **Риск:** Пункт 4.2 позволяет менять цену.\n✅ **Итог:** Высокий риск."
    },
    "Հայերեն": {
        "cur": "$", "p9": "9", "p29": "29", "mo": "/ամիս",
        "title": "Պրոֆեսիոնալ իրավական աուդիտ",
        "one_time": "Մեկանգամյա", "pro": "Անսահմանափակ Pro",
        "buy": "Գնել", "upload": "Վերբեռնել PDF պայմանագիրը",
        "btn_run": "Սկսել վերլուծությունը", "demo_tab": "📝 Օրինակ",
        "main_tab": "🚀 Վերլուծություն", "wait": "Վերբեռնեք ֆայլը...",
        "pay_msg": "🔒 Վճարեք {p} {c} ամբողջական հաշվետվության համար:",
        "risk_label": "Իրավաբանական գնահատական.",
        "demo_txt": "🔴 **Ռիսկ.** Կետ 4.2-ը թույլ է տալիս փոխել գինը:\n✅ **Եզրակացություն.** Բարձր ռիսկ:"
    }
}

# Выбор языка
c_lang, _ = st.columns([1, 4])
with c_lang:
    lang = st.selectbox("", ["English", "Русский", "Հայերեն"], label_visibility="collapsed")

t = translations[lang]

# Заголовок
st.markdown(f"<h1 style='text-align: center;'>⚖️ JurisClear AI</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: gray;'>{t['title']}</p>", unsafe_allow_html=True)

# --- 5. ТАРИФЫ ---
col1, col2 = st.columns(2)
with col1:
    st.info(f"### {t['one_time']}\n## {t['p9']} {t['cur']}")
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/checkout/buy/...") # ТВОЯ ССЫЛКА
with col2:
    st.success(f"### {t['pro']}\n## {t['p29']} {t['cur']} {t['mo']}")
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/checkout/buy/...") # ТВОЯ ССЫЛКА

st.divider()

# --- 6. ОСНОВНАЯ ЛОГИКА ---
tab_main, tab_demo = st.tabs([t['main_tab'], t['demo_tab']])

with tab_main:
    file = st.file_uploader(t['upload'], type="pdf")
    if file:
        if st.button(t['btn_run'], type="primary"):
            with st.spinner("AI Analysis in progress..."):
                reader = PdfReader(file)
                content = "".join([p.extract_text() for p in reader.pages])
                
                # Запрос к ИИ
                prompt = f"Analyze this contract in {lang}. Find 3 risks: {content[:4000]}"
                res = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.subheader(t['risk_label'])
                st.write(res.choices[0].message.content)
                st.warning(t['pay_msg'].format(p=t['p9'], c=t['cur']))
    else:
        st.info(t['wait'])

with tab_demo:
    st.markdown(t['demo_txt'])

# --- 7. ФУТЕР ---
st.divider()
st.caption(f"© 2026 JurisClear AI | Yerevan, Armenia | support@jurisclear.com")
