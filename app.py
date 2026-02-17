import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import re

# --- 1. CONFIG ---
st.set_page_config(page_title="JurisClear AI", page_icon="⚖️", layout="wide")

# --- 2. ДИНАМИЧЕСКИЙ CSS ---
def get_risk_style(score):
    """Определяет цвет и свечение в зависимости от оценки ИИ"""
    if score <= 3: # Низкий риск
        color = "linear-gradient(90deg, #059669 0%, #10b981 100%)"
        shadow = "rgba(16, 185, 129, 0.5)"
    elif score <= 6: # Средний риск
        color = "linear-gradient(90deg, #d97706 0%, #fbbf24 100%)"
        shadow = "rgba(251, 191, 36, 0.5)"
    else: # Высокий риск
        color = "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)"
        shadow = "rgba(239, 68, 68, 0.5)"
    
    return color, shadow

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 1.5rem; max-width: 1000px;}
    
    /* Тарифы */
    .pricing-card-single { background: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #3b82f6; text-align: center; color: white; }
    .pricing-card-pro { background: #064e3b; padding: 20px; border-radius: 15px; border: 1px solid #10b981; text-align: center; color: white; }
    
    /* Индикатор контейнер */
    .risk-meter-container {
        background: #0f172a; border-radius: 15px; padding: 6px;
        box-shadow: inset 0 3px 8px rgba(0,0,0,0.6); border: 1px solid #334155; margin: 15px 0;
    }
    
    .stButton>button { border-radius: 12px; height: 3.5em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ИНИЦИАЛИЗАЦИЯ ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 4. ТРАНСЛЯЦИИ ---
translations = {
    "English": {
        "cur": "$", "p9": "9", "p29": "29", "mo": "/mo",
        "buy": "Get Full Access", "upload": "Upload PDF", "btn_run": "Analyze Document",
        "risk_label": "Dynamic AI Risk Score:", "pay_msg": "🔒 Pay {p}{c} to fix these {s} risks.",
        "prompt": "Analyze this contract. Provide 3 points. END with 'SCORE: X' (where X is 1-10). Language: English."
    },
    "Русский": {
        "cur": "₽", "p9": "850", "p29": "2500", "mo": "/мес",
        "buy": "Купить доступ", "upload": "Загрузите PDF", "btn_run": "Начать анализ",
        "risk_label": "Оценка риска от ИИ:", "pay_msg": "🔒 Оплатите {p} {c}, чтобы исправить эти риски.",
        "prompt": "Проанализируй договор. Выдели 3 риска. В КОНЦЕ напиши 'SCORE: X' (где X число 1-10). Язык: Русский."
    },
    "Հայերեն": {
        "cur": "֏", "p9": "3500", "p29": "11000", "mo": "/ամիս",
        "buy": "Գնել", "upload": "Վերբեռնել PDF", "btn_run": "Սկսել",
        "risk_label": "AI Ռիսկի գնահատական.", "pay_msg": "🔒 Վճարեք {p} {c} այս ռիսկերը շտկելու համար:",
        "prompt": "Վերլուծիր պայմանագիրը: Նշիր 3 ռիսկ: ՎԵՐՋՈՒՄ գրիր 'SCORE: X' (որտեղ X-ը 1-10 թիվ է): Լեզուն՝ հայերեն:"
    }
}

lang = st.selectbox("", ["English", "Русский", "Հայերեն"], label_visibility="collapsed")
t = translations[lang]

# --- 5. HEADER ---
st.markdown(f"<h1 style='text-align: center;'>⚖️ JurisClear AI</h1>", unsafe_allow_html=True)

# Тарифы (Компактно)
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"<div class='pricing-card-single'><b>{t['cur']}{t['p9']}</b></div>", unsafe_allow_html=True)
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/...", use_container_width=True)
with c2:
    st.markdown(f"<div class='pricing-card-pro'><b>{t['cur']}{t['p29']}</b></div>", unsafe_allow_html=True)
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/...", use_container_width=True)

# --- 6. CORE LOGIC ---
file = st.file_uploader(t['upload'], type="pdf", label_visibility="collapsed")

if file:
    if st.button(t['btn_run'], type="primary", use_container_width=True):
        with st.spinner("Deep AI Audit..."):
            reader = PdfReader(file)
            text = "".join([p.extract_text() for p in reader.pages])
            
            # Запрос к ИИ
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"{t['prompt']}\n\n{text[:4000]}"}]
            )
            raw_res = response.choices[0].message.content
            
            # --- ПАРСИНГ ОЦЕНКИ ---
            score_match = re.search(r"SCORE:\s*(\d+)", raw_res)
            score = int(score_match.group(1)) if score_match else 5
            clean_res = raw_res.replace(f"SCORE: {score}", "").strip() # Убираем тех. надпись из текста
            
            # Динамические стили индикатора
            bar_color, bar_shadow = get_risk_style(score)
            width = score * 10
            
            # Вывод индикатора
            st.write(f"### {t['risk_label']}")
            st.markdown(f"""
                <div class="risk-meter-container">
                    <div style="
                        height: 30px; width: {width}%; 
                        background: {bar_color}; 
                        box-shadow: 0 0 15px {bar_shadow};
                        border-radius: 10px; display: flex; align-items: center; justify-content: center;
                        color: white; font-weight: bold; transition: width 1s ease-in-out;
                    ">
                        {score}/10
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Вывод текста анализа
            st.markdown(f"<div style='background: #1e293b; padding: 20px; border-radius: 12px; border-left: 4px solid {bar_shadow};'>{clean_res}</div>", unsafe_allow_html=True)
            
            st.warning(t['pay_msg'].format(p=t['p9'], c=t['cur'], s=score))
            st.link_button(f"🔓 {t['buy']} ({t['cur']}{t['p9']})", "https://jurisclear.lemonsqueezy.com/...", use_container_width=True)
