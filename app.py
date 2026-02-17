import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import time

# --- 1. CONFIG ---
st.set_page_config(page_title="JurisClear AI", page_icon="⚖️", layout="wide")

# --- 2. CSS: ЦВЕТНЫЕ БЛОКИ, ИНТЕРФեЙС И 3D ИНДИКАТОР ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 1.5rem; max-width: 1000px;}
    
    /* Тарифные планы */
    .pricing-card-single {
        background: linear-gradient(135deg, #1e293b 0%, #3b82f6 100%);
        padding: 25px; border-radius: 15px; border: 1px solid #60a5fa; text-align: center; color: white;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
    }
    .pricing-card-pro {
        background: linear-gradient(135deg, #064e3b 0%, #10b981 100%);
        padding: 25px; border-radius: 15px; border: 1px solid #34d399; text-align: center; color: white;
        box-shadow: 0 10px 20px rgba(16, 185, 129, 0.2);
    }
    
    /* Карточка отчета */
    .report-card {
        background-color: #1e293b; border-left: 5px solid #3b82f6;
        padding: 25px; border-radius: 12px; margin-top: 20px; color: #f1f5f9;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.2);
    }
    
    /* --- НОВЫЙ ОБЪЕМНЫЙ ИНДИКАТОР РИСКА --- */
    .risk-meter-container {
        background: #0f172a; border-radius: 15px; padding: 8px;
        box-shadow: inset 0 3px 8px rgba(0,0,0,0.6); /* Внутренняя тень для глубины */
        border: 1px solid #334155; margin-top: 10px;
    }
    .risk-bar-high {
        height: 35px; border-radius: 10px; width: 95%; /* Длина полосы */
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 50%, #f87171 100%); /* Яркий градиент */
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.5); /* Внешнее свечение для объема */
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: 900; font-size: 1.1rem; letter-spacing: 1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    
    .stButton>button {
        border-radius: 12px; height: 3.8em; font-weight: bold; transition: 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ИНИЦИАЛИЗАЦИЯ ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 4. РАЗВЕРНУТЫЕ ПРИМЕРЫ (CONTENT) ---
sample_en = """
### 📋 Audit Summary: SaaS Service Agreement
1. **Intellectual Property (Clause 5.2):** The contract states that all developments made during the term belong to the Client, but doesn't exclude pre-existing Auditor IP. 
2. **Auto-Renewal (Clause 11.4):** 30-day notice required for non-renewal. Easy to miss, leading to unwanted charges.
3. **Limitation of Liability:** Capped at 50% of fees paid. Extremely low for high-stake legal work.
"""
sample_ru = """
### 📋 Резюме аудита: Договор оказания услуг
1. **Односторонний отказ (п. 7.3):** Заказчик имеет право расторгнуть договор в любое время, оплатив только фактически понесенные расходы. Это риск внезапной потери дохода.
2. **Штрафные санкции (п. 4.1):** Пени в размере 1% в день за просрочку — это в 10 раз выше рыночной нормы (обычно 0.1%).
3. **Конфиденциальность:** Отсутствует пункт о защите персональных данных сотрудников, что может привести к штрафам от регулятора.
"""
sample_hy = """
### 📋 Աուդիտի ամփոփում. Ծառայությունների մատուցման պայմանագիր
1. **Գաղտնիություն (Կետ 9.1).** Պայմանագիրը չի սահմանում գաղտնի տեղեկատվության պաշտպանության ժամկետը պայմանագրի լուծարումից հետո:
2. **Վճարման պարտավորություններ.** Նախատեսված է տուժանք՝ ժամկետանց յուրաքանչյուր օրվա համար 0.5%, ինչը չափազանց բարձր է:
3. **Լուծարման պայմաններ.** Կողմերից մեկը կարող է միակողմանի լուծարել պայմանագիրը առանց նախնական ծանուցման:
"""

# --- 5. ТРАНСЛЯЦИИ ---
translations = {
    "English": {
        "cur": "$", "p9": "9", "p29": "29", "mo": "/mo",
        "one_time": "Single Audit", "pro": "Unlimited Pro",
        "buy": "Get Full Access", "upload": "Drag and drop PDF contract",
        "btn_run": "Run AI Analysis", "main_tab": "🚀 AI Audit", "demo_tab": "📝 See Demo",
        "risk_label": "AI Risk Assessment:", "wait": "Awaiting document...",
        "pay_to_unlock": "🔒 Unlock full legal remediation plan for {p}{c}",
        "sample": sample_en, "risk_text": "CRITICAL RISK DETECTED (9.2/10)"
    },
    "Русский": {
        "cur": "₽", "p9": "850", "p29": "2500", "mo": "/мес",
        "one_time": "Разовый аудит", "pro": "Безлимит Pro",
        "buy": "Купить доступ", "upload": "Загрузите PDF договор",
        "btn_run": "Начать анализ", "main_tab": "🚀 ИИ Аудит", "demo_tab": "📝 Пример отчета",
        "risk_label": "ИИ Оценка Риска:", "wait": "Загрузите файл для начала...",
        "pay_to_unlock": "🔒 Открыть план устранения рисков за {p} {c}",
        "sample": sample_ru, "risk_text": "ОБНАРУЖЕН КРИТИЧЕСКИЙ РИСК (9.2/10)"
    },
    "Հայերեն": {
        "cur": "֏", "p9": "3500", "p29": "11000", "mo": "/ամիս",
        "one_time": "Մեկանգամյա", "pro": "Անսահմանափակ Pro",
        "buy": "Գնել", "upload": "Վերբեռնել PDF պայմանագիրը",
        "btn_run": "Սկսել վերլուծությունը", "main_tab": "🚀 AI Աուդիտ", "demo_tab": "📝 Օրինակ",
        "risk_label": "AI Ռիսկի Գնահատական.", "wait": "Վերբեռնեք ֆայլը...",
        "pay_to_unlock": "🔒 Բացել ամբողջական վերլուծությունը {p} {c}-ով",
        "sample": sample_hy, "risk_text": "ՀԱՅՏՆԱԲԵՐՎԱԾ Է ԿՐԻՏԻԿԱԿԱՆ ՌԻՍԿ (9.2/10)"
    }
}

# Выбор языка
c_lang, _ = st.columns([1, 2])
with c_lang:
    lang = st.selectbox("", ["English", "Русский", "Հայերեն"], label_visibility="collapsed")
t = translations[lang]

# --- 6. HEADER & PRICING ---
st.markdown(f"<h1 style='text-align: center; color: white; text-shadow: 0 2px 10px rgba(59,130,246,0.5);'>⚖️ JurisClear <span style='color:#3b82f6'>AI</span></h1>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"""<div class='pricing-card-single'>
        <h3>{t['one_time']}</h3>
        <h2>{t['p9']} {t['cur']}</h2>
    </div>""", unsafe_allow_html=True)
    st.write("")
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/checkout/buy/...", use_container_width=True)

with col_b:
    st.markdown(f"""<div class='pricing-card-pro'>
        <h3>{t['pro']}</h3>
        <h2>{t['p29']} {t['cur']} <small>{t['mo']}</small></h2>
    </div>""", unsafe_allow_html=True)
    st.write("")
    st.link_button(t['buy'], "https://jurisclear.lemonsqueezy.com/checkout/buy/...", use_container_width=True)

st.divider()

# --- 7. WORKSPACE ---
tab_audit, tab_demo = st.tabs([t['main_tab'], t['demo_tab']])

with tab_audit:
    file = st.file_uploader(t['upload'], type="pdf", label_visibility="collapsed")
    if file:
        if st.button(t['btn_run'], use_container_width=True, type="primary"):
            with st.spinner("AI is analyzing your contract geometry..."):
                reader = PdfReader(file)
                text = "".join([page.extract_text() for page in reader.pages])
                
                # ИИ Запрос
                prompt = f"Act as a top-tier lawyer. Analyze this contract in {lang}. List 3 critical risks briefly. Text: {text[:4000]}"
                response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
                result = response.choices[0].message.content
                
                st.markdown(f"### 🛡️ {t['main_tab']}")
                
                # --- НОВЫЙ ОБЪЕМНЫЙ ИНДИКАТОР (Внедрение) ---
                st.write(t['risk_label'])
                st.markdown(f"""
                <div class="risk-meter-container">
                    <div class="risk-bar-high">
                        ⚠️ {t['risk_text']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # -------------------------------------------
                
                st.markdown(f"<div class='report-card'>{result}</div>", unsafe_allow_html=True)
                
                st.warning(t['pay_to_unlock'].format(p=t['p9'], c=t['cur']))
                st.link_button(f"👉 {t['buy']} ({t['p9']} {t['cur']})", "https://jurisclear.lemonsqueezy.com/checkout/buy/...", use_container_width=True)
    else:
        st.info(t['wait'])

with tab_demo:
    st.markdown(f"### {t['demo_tab']}")
    st.markdown("---")
    
    # --- ДЕМО ОБЪЕМНОГО ИНДИКАТОРА ---
    st.write(t['risk_label'])
    st.markdown(f"""
    <div class="risk-meter-container">
        <div class="risk-bar-high">
            ⚠️ {t['risk_text']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ---------------------------------
    
    st.markdown(f"<div class='report-card'>{t['sample']}</div>", unsafe_allow_html=True)
    st.info("💡 This sample demonstrates a typical high-risk analysis outcome.")

# --- 8. FOOTER ---
st.divider()
st.caption(f"© 2026 JurisClear AI | Yerevan, Armenia | support@jurisclear.com")
