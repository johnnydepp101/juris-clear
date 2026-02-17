import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

# --- 1. ТЕХНИЧЕСКАЯ НАСТРОЙКА (ДОЛЖНА БЫТЬ ПЕРВОЙ) ---
st.set_page_config(
    page_title="JurisClear AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. СКРЫТИЕ БРЕНДИНГА (ЧИСТЫЙ ИНТЕРФЕЙС) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    /* Стилизация кнопок оплаты */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        font-weight: bold;
        background-color: #3b82f6;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        transform: scale(1.02);
    }
    /* Убираем рамки и лишние кнопки */
    button[title="View fullscreen"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ПОДКЛЮЧЕНИЕ API ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Ошибка: Проверьте API Key в настройках Streamlit Cloud.")

# --- 4. СЛОВАРЬ (ТЕКСТ + ЦЕНЫ + ВАЛЮТЫ) ---
# Здесь мы жестко связываем язык с валютой, чтобы ты видел изменения
translations = {
    "English": {
        "cur": "$", "p9": "9", "p29": "29", "mo": "/mo",
        "title": "Professional Legal Audit",
        "one_time": "Single Audit", "pro": "Unlimited Pro",
        "buy": "Get Started", "upload": "Upload PDF Contract",
        "btn_run": "Run AI Analysis", "demo_tab": "📝 Sample Report",
        "main_tab": "🚀 Analysis", "wait": "Please upload a document...",
        "pay_msg": "🔒 Pay {p}{c} to unlock full report.",
        "risk_label": "Legal Assessment:",
        "demo_txt": "🔴 **Critical Risk:** Price changes allowed without notice.\n\n✅ **Verdict:** High Risk."
    },
    "Русский": {
        "cur": "₽", "p9": "850", "p29": "2500", "mo": "/мес",
        "title": "Профессиональный юридический аудит",
        "one_time": "Разовый аудит", "pro": "Безлимит Pro",
        "buy": "Купить доступ", "upload": "Загрузите PDF договор",
        "btn_run": "Начать анализ", "demo_tab": "📝 Пример отчета",
        "main_tab": "🚀 Анализ", "wait": "Загрузите файл...",
        "pay_msg": "🔒 Оплатите {p} {c}, чтобы открыть полный отчет.",
        "risk_label": "Юридический анализ:",
        "demo_txt": "🔴 **Риск:** Изменение цены в одностороннем порядке.\n\n✅ **Итог:** Высокий риск."
    },
    "Հայերեն": {
        "cur": "֏", "p9": "3500", "p29": "11000", "mo": "/ամիս",
        "title": "Պրոֆեսիոնալ իրավական աուդիտ",
        "one_time": "Մեկանգամյա", "pro": "Անսահմանափակ Pro",
        "buy": "Գնել", "upload": "Վերբեռնել PDF պայմանագիրը",
        "btn_run": "Սկսել վերլուծությունը", "demo_tab": "📝 Օրինակ",
        "main_tab": "🚀 Վերլուծություն", "wait": "Վերբեռնեք ֆայլը...",
        "pay_msg": "🔒 Վճարեք {p} {c} ամբողջական հաշվետվության համար:",
        "risk_label": "Իրավաբանական գնահատական.",
        "demo_txt": "🔴 **Ռիսկ.** Գնի միակողմանի փոփոխություն:\n\n✅ **Եզրակացություն.** Բարձր ռիսկ:"
    }
}

# --- 5. ВЫБОР ЯЗЫКА ---
c1, _ = st.columns([1, 3])
with c1:
    # Здесь происходит магия: при выборе языка скрипт перезапускается с новыми данными
    lang = st.selectbox("Language / Язык", ["English", "Русский", "Հայերեն"], label_visibility="collapsed")

t = translations[lang]

# --- 6. ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---
st.markdown(f"<h1 style='text-align: center;'>⚖️ JurisClear AI</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: gray; font-size: 1.2rem;'>{t['title']}</p>", unsafe_allow_html=True)

# Секция тарифов
col_a, col_b = st.columns(2)
with col_a:
    st.info(f"### {t['one_time']}\n## {t['p9']} {t['cur']}")
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/checkout/buy/...") 
with col_b:
    st.success(f"### {t['pro']}\n## {t['p29']} {t['cur']} {t['mo']}")
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/checkout/buy/...")

st.write("")

# Вкладки анализа
tab_work, tab_sample = st.tabs([t['main_tab'], t['demo_tab']])

with tab_work:
    uploaded_file = st.file_uploader(t['upload'], type="pdf", label_visibility="collapsed")
    
    if uploaded_file:
        if st.button(t['btn_run']):
            with st.spinner("AI Analysis in progress..."):
                # Читаем текст PDF
                pdf_reader = PdfReader(uploaded_file)
                contract_text = ""
                for page in pdf_reader.pages:
                    contract_text += page.extract_text()
                
                # Запрос к ИИ
                try:
                    prompt = f"Analyze this contract for 3 risks in {lang}: {contract_text[:4000]}"
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    st.subheader(t['risk_label'])
                    st.markdown(response.choices[0].message.content)
                    st.divider()
                    
                    # Финальный призыв к оплате
                    st.warning(t['pay_msg'].format(p=t['p9'], c=t['cur']))
                    st.link_button(f"👉 {t['buy']} ({t['p9']} {t['cur']})", "https://jurisclear.lemonsqueezy.com/checkout/buy/...")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info(t['wait'])

with tab_sample:
    st.markdown(t['demo_txt'])

# --- 7. ФУТЕР (ПРОФЕССИОНАЛЬНЫЙ ФИНАЛ) ---
st.write("")
st.divider()
st.caption(f"© 2026 JurisClear AI | support@jurisclear.com | Yerevan, Armenia")
