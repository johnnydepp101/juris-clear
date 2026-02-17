import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import re

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="JurisClear AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ВЕСЬ ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 1.5rem; max-width: 1000px;}
    
    /* Тарифные планы */
    .pricing-card-single {
        background: linear-gradient(135deg, #1e293b 0%, #3b82f6 100%);
        padding: 20px; border-radius: 15px; border: 1px solid #60a5fa; text-align: center; color: white;
    }
    .pricing-card-pro {
        background: linear-gradient(135deg, #064e3b 0%, #10b981 100%);
        padding: 20px; border-radius: 15px; border: 1px solid #34d399; text-align: center; color: white;
    }
    
    /* Карточка отчета */
    .report-card {
        background-color: #1e293b; border-left: 5px solid #3b82f6;
        padding: 25px; border-radius: 12px; margin-top: 20px; color: #f1f5f9;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.2);
    }
    
    /* Объемный контейнер для шкалы риска */
    .risk-meter-container {
        background: #0f172a; border-radius: 15px; padding: 8px;
        box-shadow: inset 0 3px 8px rgba(0,0,0,0.6); border: 1px solid #334155; margin: 15px 0;
    }
    
    .stButton>button {
        border-radius: 12px; height: 3.8em; font-weight: bold; transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ЛОГИКА ДИНАМИЧЕСКОЙ ШКАЛЫ ---
def get_risk_params(score):
    if score <= 3:
        return "linear-gradient(90deg, #059669 0%, #10b981 100%)", "rgba(16, 185, 129, 0.5)", "НИЗКИЙ"
    elif score <= 6:
        return "linear-gradient(90deg, #d97706 0%, #fbbf24 100%)", "rgba(251, 191, 36, 0.5)", "СРЕДНИЙ"
    else:
        return "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)", "rgba(239, 68, 68, 0.5)", "КРИТИЧЕСКИЙ"

# --- 4. ПОДКЛЮЧЕНИЕ API И ПРИМЕР (ОБНОВЛЕН) ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === НОВЫЙ ПРОФЕССИОНАЛЬНЫЙ ПРИМЕР ОТЧЕТА ===
sample_text = """
### 📋 КРАТКОЕ РЕЗЮМЕ АУДИТА: ДОГОВОР ОКАЗАНИЯ УСЛУГ

**ОБЩИЙ ВЕРДИКТ:** Договор составлен с существенным перекосом баланса интересов в пользу Исполнителя и содержит условия, способные нанести значительный финансовый ущерб Заказчику. Настоятельно рекомендуется доработка перед подписанием.

---

#### 1. ФИНАНСОВЫЕ РИСКИ И ОТВЕТСТВЕННОСТЬ

**🔴 Критическая угроза: Кабальная неустойка (Пункт 6.1)**
* **Суть условия:** Установлена пеня за просрочку оплаты в размере **1% в день** от суммы задолженности.
* **Юридический анализ:** Это эквивалентно **365% годовых**, что более чем в 10 раз превышает стандартную деловую практику (обычно 0,1%). Суд с высокой вероятностью признает такую неустойку несоразмерной, но до этого момента вы будете накапливать огромный долг. Риск потери ликвидности.

**🟠 Высокая угроза: Неконтролируемое изменение цены (Пункт 4.2)**
* **Суть условия:** Исполнитель имеет право в одностороннем порядке повышать стоимость услуг, уведомив Заказчика за 5 рабочих дней.
* **Юридический анализ:** Отсутствует механизм согласования новой цены или безусловное право Заказчика на расторжение договора без штрафов в случае несогласия с новой ценой. Риск непланируемых расходов.

#### 2. РИСКИ РАСТОРЖЕНИЯ И РАЗРЕШЕНИЯ СПОРОВ

**🟡 Средняя угроза: Невыгодная договорная подсудность (Пункт 9.3)**
* **Суть условия:** Все споры по договору подлежат рассмотрению в арбитражном суде по месту нахождения Исполнителя (г. Владивосток).
* **Юридический анализ:** Это существенно усложняет и удорожает процесс защиты ваших прав (транспортные расходы, наем локальных представителей), если ваша компания находится в другом регионе.

*💡 (Примечание: Полная версия отчета содержит конкретные формулировки правок (протокол разногласий) для нейтрализации каждого из указанных рисков.)*
"""
# ============================================

# --- 5. ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---
st.markdown(f"<h1 style='text-align: center; color: white;'>⚖️ JurisClear <span style='color:#3b82f6'>AI</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Профессиональный юридический аудит договоров</p>", unsafe_allow_html=True)

# Секция цен
col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"<div class='pricing-card-single'><h3>Разовый аудит</h3><h2>850 ₽</h2></div>", unsafe_allow_html=True)
    st.write("")
    st.link_button("Купить доступ", "https://jurisclear.lemonsqueezy.com/checkout/buy/...", use_container_width=True)
with col_b:
    st.markdown(f"<div class='pricing-card-pro'><h3>Безлимит Pro</h3><h2>2500 ₽ <small>/мес</small></h2></div>", unsafe_allow_html=True)
    st.write("")
    st.link_button("Купить доступ", "https://jurisclear.lemonsqueezy.com/checkout/buy/...", use_container_width=True)

st.divider()

# Рабочее пространство (Вкладки)
tab_audit, tab_demo = st.tabs(["🚀 ИИ Аудит", "📝 Пример отчета"])

with tab_audit:
    file = st.file_uploader("Загрузите PDF договор", type="pdf", label_visibility="collapsed")
    if file:
        if st.button("Начать анализ", use_container_width=True, type="primary"):
            with st.spinner("ИИ проводит глубокий юридический аудит..."):
                reader = PdfReader(file)
                text = "".join([p.extract_text() for p in reader.pages])
                
                # Запрос к ИИ с жестким требованием оценки
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Проанализируй договор. Выдели 3 самых критичных риска. В самом конце ответа обязательно напиши фразу 'SCORE: X' (где X — число от 1 до 10). Язык: Русский.\n\nТекст договора:\n{text[:4000]}"}]
                )
                raw_res = response.choices[0].message.content
                
                # Парсинг оценки для шкалы
                score_match = re.search(r"SCORE:\s*(\d+)", raw_res)
                score = int(score_match.group(1)) if score_match else 5
                # Чистим текст от технической метки SCORE
                clean_res = re.sub(r"SCORE:\s*\d+", "", raw_res).strip()
                
                # Параметры динамической шкалы
                bar_color, bar_shadow, risk_text = get_risk_params(score)
                
                st.write("### ИИ Оценка Риска:")
                st.markdown(f"""
                    <div class="risk-meter-container">
                        <div style="height:35px; width:{score*10}%; background:{bar_color}; 
                        box-shadow: 0 4px 15px {bar_shadow}; border-radius:10px; 
                        display:flex; align-items:center; justify-content:center; color:white; font-weight:900;">
                            {risk_text} ({score}/10)
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"<div class='report-card'>{clean_res}</div>", unsafe_allow_html=True)
                
                st.warning(f"🔒 Чтобы получить полный план устранения этих рисков, оплатите 850 ₽.")
                st.link_button(f"👉 Оплатить и исправить риски", "https://jurisclear.lemonsqueezy.com/checkout/buy/...", use_container_width=True)
    else:
        st.info("Пожалуйста, загрузите файл договора в формате PDF для начала анализа.")

with tab_demo:
    st.write("### Так выглядит результат анализа:")
    # Статичный пример для демонстрации
    bar_color, bar_shadow, risk_text = get_risk_params(9)
    st.markdown(f"""
        <div class="risk-meter-container">
            <div style="height:35px; width:90%; background:{bar_color}; 
            box-shadow: 0 4px 15px {bar_shadow}; border-radius:10px; 
            display:flex; align-items:center; justify-content:center; color:white; font-weight:900;">
                КРИТИЧЕСКИЙ (9/10)
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<div class='report-card'>{sample_text}</div>", unsafe_allow_html=True)

st.divider()
st.caption("© 2026 JurisClear AI | Ереван, Армения | support@jurisclear.com")
