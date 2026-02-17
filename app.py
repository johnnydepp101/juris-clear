import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

# --- 1. CONFIG (Должен быть первым!) ---
st.set_page_config(
    page_title="JurisClear AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. SECURITY & API ---
# Используем секреты Streamlit для безопасности
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API Key missing! Please add it to Streamlit Secrets.")

# --- 3. PROFESSIONAL STYLING (Hiding Streamlit branding) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    .stButton>button {width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; background-color: #3b82f6; color: white; border: none;}
    .stButton>button:hover {background-color: #2563eb; border: none;}
    /* Прячем кнопку Fullscreen */
    button[title="View fullscreen"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. TRANSLATIONS & PRICING LOGIC ---
translations = {
    "English": {
        "cur": "$", "p9": "9", "p29": "29", "mo": "/mo",
        "subtitle": "Professional Legal Document Audit",
        "one_time": "Single Audit", "pro": "Unlimited Pro",
        "buy": "Buy Access", "upload": "Upload PDF Contract",
        "btn_run": "Start Analysis", "demo_tab": "📝 Sample Report",
        "main_tab": "🚀 AI Analysis", "wait": "Please upload a PDF file...",
        "pay_msg": "🔒 Pay {p}{c} to unlock the full legal report.",
        "risk_label": "Legal Risk Assessment:",
        "demo_txt": "🔴 **Critical Risk:** Clause 8.2 allows termination without notice.\n\n🟠 **Medium Risk:** Intellectual property rights are poorly defined.\n\n✅ **Verdict:** High risk. Review needed."
    },
    "Русский": {
        "cur": "$", "p9": "9", "p29": "29", "mo": "/мес.",
        "subtitle": "Профессиональный юридический аудит документов",
        "one_time": "Разовый аудит", "pro": "Безлимит Pro",
        "buy": "Купить доступ", "upload": "Загрузите PDF договор",
        "btn_run": "Начать анализ", "demo_tab": "📝 Пример отчета",
        "main_tab": "🚀 ИИ Анализ", "wait": "Загрузите PDF файл для начала...",
        "pay_msg": "🔒 Оплатите {p}{c}, чтобы открыть полный отчет.",
        "risk_label": "Результат анализа:",
        "demo_txt": "🔴 **Критический риск:** Пункт 8.2 позволяет расторгнуть договор без уведомления.\n\n🟠 **Средний риск:** Права на интеллектуальную собственность размыты.\n\n✅ **Итог:** Высокий риск. Требуются правки."
    },
    "Հայերեն": {
        "cur": "$", "p9": "9", "p29": "29", "mo": "/ամիս",
        "subtitle": "Փաստաթղթերի մասնագիտական իրավական աուդիտ",
        "one_time": "Մեկանգամյա", "pro": "Անսահմանափակ Pro",
        "buy": "Գնել", "upload": "Վերբեռնել PDF պայմանագիրը",
        "btn_run": "Սկսել վերլուծությունը", "demo_tab": "📝 Օրինակ",
        "main_tab": "🚀 AI Վերլուծություն", "wait": "Վերբեռնեք PDF ֆայլը...",
        "pay_msg": "🔒 Վճարեք {p}{c} ամբողջական հաշվետվության համար:",
        "risk_label": "Իրավաբանական գնահատական.",
        "demo_txt": "🔴 **Կրիտիկական ռիսկ.** Կետ 8.2-ը թույլ է տալիս լուծարել պայմանագիրը առանց ծանուցման:\n\n🟠 **Միջին ռիսկ.** Մտավոր սեփականության իրավունքները հստակ չեն:\n\n✅ **Եզրակացություն.** Բարձր ռիսկ:"
    }
}

# Выбор языка
c_lang, _ = st.columns([1, 3])
with c_lang:
    lang = st.selectbox("", ["English", "Русский", "Հայերեն"], label_visibility="collapsed")

t = translations[lang]

# Шапка
st.markdown(f"<h1 style='text-align: center;'>⚖️ JurisClear AI</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: gray;'>{t['subtitle']}</p>", unsafe_allow_html=True)

# --- 5. PRICING SECTION ---
col1, col2 = st.columns(2)
with col1:
    st.info(f"### {t['one_time']}\n## {t['p9']}{t['cur']}")
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/checkout/buy/9usd-id") # ЗАМЕНИ НА СВОЮ
with col2:
    st.success(f"### {t['pro']}\n## {t['p29']}{t['cur']}{t['mo']}")
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/checkout/buy/29usd-id") # ЗАМЕНИ НА СВОЮ

st.write("")

# --- 6. MAIN LOGIC ---
tab1, tab2 = st.tabs([t['main_tab'], t['demo_tab']])

with tab1:
    file = st.file_uploader(t['upload'], type="pdf", label_visibility="collapsed")
    if file:
        if st.button(t['btn_run']):
            with st.spinner("AI Analysis..."):
                # Чтение текста
                pdf = PdfReader(file)
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                
                # Запрос к OpenAI
                try:
                    prompt = f"Analyze this contract in {lang}. Find 3 main risks: {text[:4000]}"
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.subheader(t['risk_label'])
                    st.markdown(response.choices[0].message.content)
                    st.divider()
                    st.warning(t['pay_msg'].format(p=t['p9'], c=t['cur']))
                    st.link_button(f"👉 {t['buy']} ({t['p9']}{t['cur']})", "https://jurisclear.lemonsqueezy.com/checkout/buy/9usd-id")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info(t['wait'])

with tab2:
    st.markdown(t['demo_txt'])

# --- 7. FOOTER ---
st.write("")
st.divider()
st.caption(f"© 2026 JurisClear AI | support@jurisclear.com | Yerevan, Armenia")
