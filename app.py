import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

# --- 1. ТВОИ НАСТРОЙКИ ---
LINK_9USD = "https://jurisclearai.lemonsqueezy.com/checkout/buy/a06e3832-bc7a-4d2c-8f1e-113446b2bf61"
LINK_29USD = "https://jurisclearai.lemonsqueezy.com/checkout/buy/69a180c9-d5f5-4018-9dbe-b8ac64e4ced8"

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("OpenAI API Key not found in Secrets")

# --- 2. ЛОГИКА ИИ (Исправленная версия 1.0+) ---
def get_ai_analysis(text, lang):
    prompts = {
        "Русский": "Ты профессиональный юрист. Проанализируй этот текст договора. Найди 3 главных юридических риска и дай общую оценку безопасности от 1 до 10. Отвечай на русском.",
        "English": "You are a professional lawyer. Analyze this contract text. Find 3 main risks and give an overall safety score from 1 to 10. Answer in English.",
        "Հայերեն": "Դուք պրոֆեսիոնալ իրավաբան եք: Վերլուծեք պայմանագիրը: Գտեք 3 հիմնական ռիսկերը և տվեք անվտանգության գնահատական 1-ից 10-ը: Պատասխանեք հայերեն:"
    }
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional legal auditor."},
                {"role": "user", "content": f"{prompts[lang]}\n\n{text[:4000]}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- 3. ПОЛНЫЙ СЛОВАРЬ (Вернули всё!) ---
translations = {
    "English": {
        "cur": "$", "rate": 1, "mo": "/ mo", "title": "JurisClear AI",
        "subtitle": "Next-Gen Legal Document Audit", "one_time": "Single Audit",
        "pro": "Unlimited Pro", "price_9": "9", "price_29": "29", "buy": "Get Started",
        "upload": "Upload PDF contract", "demo_tab": "📝 Sample Report", "main_tab": "🚀 Analysis",
        "risk_score_label": "Risk Assessment Score:", "risk_desc": "7/10 - Attention Required",
        "btn_run": "Start AI Analysis", "wait_msg": "Please upload a document...",
        "pay_to_unlock": "🔒 Pay {price} {cur} to unlock full details.",
        "demo_content": "🔴 **Critical Risk:** Clause 4.2 allows price changes without notice.\n\n🟠 **Medium Risk:** Deposit return terms are vague.\n\n✅ **Verdict:** Do not sign without amendments."
    },
    "Русский": {
        "cur": "₽", "rate": 90, "mo": "/ мес.", "title": "JurisClear AI",
        "subtitle": "Юридический аудит нового поколения", "one_time": "Разовый аудит",
        "pro": "Безлимит Pro", "price_9": "810", "price_29": "2610", "buy": "Купить доступ",
        "upload": "Загрузите PDF договор", "demo_tab": "📝 Пример отчета", "main_tab": "🚀 Анализ",
        "risk_score_label": "Оценка юридического риска:", "risk_desc": "7/10 - Требуется внимание",
        "btn_run": "Запустить ИИ анализ", "wait_msg": "Загрузите документ для начала...",
        "pay_to_unlock": "🔒 Оплатите {price} {cur}, чтобы открыть отчет.",
        "demo_content": "🔴 **Критический риск:** Пункт 4.2 позволяет менять цену без уведомления.\n\n🟠 **Средний риск:** Условия возврата депозита размыты.\n\n✅ **Итог:** Не подписывайте без правок."
    },
    "Հայերեն": {
        "cur": "֏", "rate": 400, "mo": "/ ամիս", "title": "JurisClear AI",
        "subtitle": "Իրավաբանական աուդիտի նոր սերունդ", "one_time": "Մեկանգամյա ստուգում",
        "pro": "Անսահմանափակ Pro", "price_9": "3600", "price_29": "11600", "buy": "Գնել",
        "upload": "Վերբեռնել PDF պայմանագիրը", "demo_tab": "📝 Օրինակ", "main_tab": "🚀 Վերլուծություն",
        "risk_score_label": "Իրավաբանական ռիսկի գնահատականը.", "risk_desc": "7/10 - Պահանջվում է ուշադրություն",
        "btn_run": "Սկսել վերլուծությունը", "wait_msg": "Վերբեռնեք փաստաթուղթը...",
        "pay_to_unlock": "🔒 Վճարեք {price} {cur} ամբողջական հաշվետվության համար:",
        "demo_content": "🔴 **Կրիտիկական ռիսկ.** 4.2 կետը թույլ է տալիս փոխել գինը առանց ծանուցման:\n\n🟠 **Միջին ռիսկ.** Ավանդի վերադարձի պայմանները անորոշ են:\n\n✅ **Եզրակացություն.** Մի ստորագրեք առանց փոփոխությունների:"
    }
}

st.set_page_config(page_title="JurisClear AI", page_icon="⚖️", layout="wide")

# ШАПКА И ВЫБОР ЯЗЫКА (БЕЗ МИГАНИЯ)
st.markdown("<style>div.row-widget.stRadio > div{flex-direction:row; justify-content: flex-end;}</style>", unsafe_allow_html=True)
h_left, h_right = st.columns([3, 1])
with h_left:
    st.markdown(f"# ⚖️ JurisClear AI")
with h_right:
    lang_choice = st.radio("", ["Русский", "English", "Հայերեն"], label_visibility="collapsed")
    t = translations[lang_choice]

st.markdown(f"#### *{t['subtitle']}*")
st.divider()

# ТАРИФЫ
c1, c2 = st.columns(2)
with c1:
    st.info(f"### {t['one_time']}\n## {t['price_9']} {t['cur']}")
    st.link_button(t['buy'], LINK_9USD, use_container_width=True)
with c2:
    st.success(f"### {t['pro']}\n## {t['price_29']} {t['cur']} {t['mo']}")
    st.link_button(t['buy'], LINK_29USD, use_container_width=True)

# РАБОЧАЯ ОБЛАСТЬ
tab1, tab2 = st.tabs([t['main_tab'], t['demo_tab']])

with tab1:
    file = st.file_uploader(t['upload'], type="pdf")
    if file:
        if st.button(t['btn_run'], type="primary"):
            with st.spinner("AI analyzing..."):
                reader = PdfReader(file)
                text = "".join([p.extract_text() for p in reader.pages])
                analysis = get_ai_analysis(text, lang_choice)
                
                st.subheader(t['risk_score_label'])
                st.markdown(analysis)
                st.divider()
                st.warning(t['pay_to_unlock'].format(price=t['price_9'], cur=t['cur']))
                st.link_button(f"👉 {t['buy']}", LINK_9USD)
    else:
        st.write(t['wait_msg'])

with tab2:
    st.markdown(f"### {t['demo_tab']}")
    st.info(t['demo_content'])

st.divider()
f1, f2, f3 = st.columns(3)
with f1:
    st.write("© 2026 JurisClear AI")
with f2:
    st.write("Contact: support@jurisclear.ai") # Или твой личный email
with f3:
    st.write("Yerevan, Armenia")
st.caption("JurisClear AI © 2026")
