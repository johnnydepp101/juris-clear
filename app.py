import streamlit as st
import openai
from PyPDF2 import PdfReader

# --- 1. ТВОИ НАСТРОЙКИ ---
# ВСТАВЬ СВОИ ССЫЛКИ ИЗ LEMONSQUEEZY МЕЖДУ КАВЫЧКАМИ
LINK_9USD = "https://jurisclearai.lemonsqueezy.com/checkout/buy/a06e3832-bc7a-4d2c-8f1e-113446b2bf61"
LINK_29USD = "https://jurisclearai.lemonsqueezy.com/checkout/buy/69a180c9-d5f5-4018-9dbe-b8ac64e4ced8"

# Подключение OpenAI из Secrets
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("Ошибка: API ключ не найден в Secrets!")

# --- 2. ЛОГИКА ИИ ---
def get_ai_analysis(text, lang):
    """Функция отправки текста договора в OpenAI"""
    prompts = {
        "Русский": "Ты профессиональный юрист. Проанализируй этот текст договора. Найди 3 главных юридических риска и дай общую оценку безопасности от 1 до 10.",
        "English": "You are a professional lawyer. Analyze this contract text. Find the 3 main legal risks and give an overall safety score from 1 to 10.",
        "Հայերեն": "Դուք պրոֆեսիոնալ իրավաբան եք: Վերլուծեք պայմանագրի այս տեքստը: Գտեք 3 հիմնական իրավաբանական ռիսկերը և տվեք անվտանգության ընդհանուր գնահատական 1-ից 10-ը:"
    }
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # Или gpt-4, если позволяет баланс
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": f"{prompts[lang]}\n\n{text[:4000]}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- 3. ИНТЕРФЕЙС И СЛОВАРЬ ---
translations = {
    "English": {
        "cur": "$", "rate": 1, "mo": "/ mo", "title": "JurisClear AI",
        "subtitle": "Next-Gen Legal Document Audit", "one_time": "Single Audit",
        "pro": "Unlimited Pro", "price_9": "9", "price_29": "29", "buy": "Unlock Full Analysis",
        "upload": "Upload PDF contract", "demo_tab": "📝 Sample", "main_tab": "🚀 Analysis",
        "risk_score": "Risk Assessment", "status_ready": "✅ Document analyzed.",
        "btn_run": "Start AI Analysis"
    },
    "Русский": {
        "cur": "₽", "rate": 90, "mo": "/ мес.", "title": "JurisClear AI",
        "subtitle": "Юридический аудит нового поколения", "one_time": "Разовый аудит",
        "pro": "Безлимит Pro", "price_9": "810", "price_29": "2610", "buy": "Открыть полный отчет",
        "upload": "Загрузите PDF договор", "demo_tab": "📝 Пример", "main_tab": "🚀 Анализ",
        "risk_score": "Оценка рисков", "status_ready": "✅ Документ проанализирован.",
        "btn_run": "Запустить ИИ анализ"
    },
    "Հայերեն": {
        "cur": "֏", "rate": 400, "mo": "/ ամիս", "title": "JurisClear AI",
        "subtitle": "Իրավաբանական աուդիտի նոր սերունդ", "one_time": "Մեկանգամյա ստուգում",
        "pro": "Անսահմանափակ Pro", "price_9": "3600", "price_29": "11600", "buy": "Բացել ամբողջական հաշվետվությունը",
        "upload": "Վերբեռնել PDF պայմանագիրը", "demo_tab": "📝 Օրինակ", "main_tab": "🚀 Վերլուծություն",
        "risk_score": "Ռիսկերի գնահատում", "status_ready": "✅ Փաստաթուղթը վերլուծված է:",
        "btn_run": "Սկսել վերլուծությունը"
    }
}

st.set_page_config(page_title="JurisClear AI", page_icon="⚖️", layout="wide")

# Выбор языка
h_left, h_right = st.columns([3, 1])
with h_right:
    lang_choice = st.radio("", ["Русский", "English", "Հայերեն"], label_visibility="collapsed", horizontal=True)
    t = translations[lang_choice]

with h_left:
    st.markdown(f"# ⚖️ {t['title']}")
    st.caption(t['subtitle'])

st.divider()

# Тарифы
col1, col2 = st.columns(2)
with col1:
    st.info(f"### {t['one_time']}\n## {t['price_9']} {t['cur']}")
    st.link_button("Get Started", LINK_9USD, use_container_width=True)
with col2:
    st.success(f"### {t['pro']}\n## {t['price_29']} {t['cur']} {t['mo']}")
    st.link_button("Get Started", LINK_29USD, use_container_width=True)

# Основной блок
tab_main, tab_demo = st.tabs([t['main_tab'], t['demo_tab']])

with tab_main:
    uploaded_file = st.file_uploader(t['upload'], type="pdf")
    
    if uploaded_file:
        # Извлечение текста
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()
        
        if st.button(t['btn_run'], type="primary"):
            with st.spinner("AI is thinking..."):
                analysis = get_ai_analysis(full_text, lang_choice)
                
                st.subheader(t['risk_score'])
                st.write(analysis)
                
                st.write("---")
                st.warning(f"💡 {t['buy']}")
                st.link_button(f"👉 {t['buy']}", LINK_9USD)

with tab_demo:
    st.write("Example report content...")

st.divider()
st.caption("JurisClear AI © 2026")
