import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import pdfplumber
import re
from supabase import create_client, Client  # Добавили импорт Supabase
import os
from fpdf import FPDF

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="JurisClear AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

# --- ИНИЦИАЛИЗАЦИЯ ПОЛЬЗОВАТЕЛЯ ---
if 'user' not in st.session_state:
    st.session_state.user = None

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
    /* Ультимативное выравнивание кнопок */
    .stButton > button, .stLinkButton > a {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 50px !important; /* Фиксированная высота */
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        border-radius: 10px !important;
        text-decoration: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    /* Цвет для кнопки-ссылки (Оплатить), чтобы она была как Primary */
    .stLinkButton > a {
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
    }
    .stLinkButton > a:hover {
        background-color: #2563eb !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
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

# --- 4. ПОДКЛЮЧЕНИЕ API И БАЗЫ ДАННЫХ ---
# OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Функция для выхода
def sign_out():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# --- ФУНКЦИЯ СОЗДАНИЯ PDF ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    
    # Путь к шрифту
    font_path = "DejaVuSans.ttf" 
    
    if os.path.exists(font_path):
        pdf.add_font('DejaVu', '', font_path)
        pdf.set_font('DejaVu', '', 12)
    else:
        # Если вдруг файла нет, будет Arial (но русский не отобразится)
        pdf.set_font("Arial", size=12)
    
    clean_text = text.replace("[PAYWALL]", "").strip()
    
    # Умная разбивка текста на строки
    for line in clean_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)
    
    return pdf.output() # Для fpdf2 это вернет байты

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

# --- 5. ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---

# --- ХЕДЕР ПРИЛОЖЕНИЯ ---
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown(f"<h1 style='color: white;'>⚖️ JurisClear <span style='color:#3b82f6'>AI</span></h1>", unsafe_allow_html=True)

with header_col2:
    # Если пользователь не вошел
    if st.session_state.user is None:
        with st.popover("👤 Войти", use_container_width=True):
            tab_login, tab_signup = st.tabs(["Вход", "Регистрация"])
            
            with tab_login:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Пароль", type="password", key="login_pass")
                if st.button("Войти", use_container_width=True, type="primary"):
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = res.user
                        st.success("Успешный вход!")
                        st.rerun()
                    except Exception as e:
                        st.error("Ошибка входа: проверьте данные")
            
            with tab_signup:
                new_email = st.text_input("Email", key="reg_email")
                new_pass = st.text_input("Пароль", type="password", key="reg_pass")
                if st.button("Создать аккаунт", use_container_width=True):
                    try:
                        res = supabase.auth.sign_up({"email": new_email, "password": new_pass})
                        st.info("Проверьте почту для подтверждения регистрации!")
                    except Exception as e:
                        st.error(f"Ошибка: {e}")
    else:
        # Если пользователь вошел
        user_email = st.session_state.user.email
        with st.popover(f"👤 {user_email[:10]}...", use_container_width=True):
            st.write(f"Вы вошли как: **{user_email}**")
            if st.button("Выйти", use_container_width=True):
                sign_out()

st.markdown("<p style='text-align: center; color: gray;'>Профессиональный юридический аудит договоров</p>", unsafe_allow_html=True)

# Секция цен
col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"<div class='pricing-card-single'><h3>Разовый аудит</h3><h2>850 ₽</h2></div>", unsafe_allow_html=True)
    st.write("")
    st.link_button("Купить доступ", "https://jurisclearai.lemonsqueezy.com/checkout/buy/a06e3832-bc7a-4d2c-8f1e-113446b2bf61", use_container_width=True)
with col_b:
    st.markdown(f"<div class='pricing-card-pro'><h3>Безлимит Pro</h3><h2>2500 ₽ <small>/мес</small></h2></div>", unsafe_allow_html=True)
    st.write("")
    st.link_button("Купить доступ", "https://jurisclearai.lemonsqueezy.com/checkout/buy/69a180c9-d5f5-4018-9dbe-b8ac64e4ced8", use_container_width=True)

st.divider()

# Параметры анализа
st.markdown("### ⚙️ Параметры анализа")
c1, c2 = st.columns(2)

with c1:
    st.write("**Ваша роль:**")
    user_role = st.pills(
        "Роль", 
        [
            "Заказчик", "Исполнитель", 
            "Покупатель", "Поставщик", 
            "Арендатор", "Арендодатель", 
            "Работник", "Работодатель", 
            "Инвестор", "Основатель",
            "Лицензиат", "Лицензиар"
        ], 
        selection_mode="single", 
        default="Заказчик",
        label_visibility="collapsed"
    )

with c2:
    st.write("**Тип документа:**")
    contract_type = st.pills(
        "Тип", 
        [
            "Авто-определение", "Услуги", 
            "Поставка / Купля-продажа", "NDA", 
            "Аренда", "Трудовой", 
            "ИТ-разработка", "Лицензионный", 
            "Займ", "Агентский"
        ], 
        selection_mode="single", 
        default="Авто-определение",
        label_visibility="collapsed"
    )

# Рабочее пространство (Вкладки)
tab_audit, tab_demo, tab_history = st.tabs(["🚀 ИИ Аудит", "📝 Пример отчета", "📜 История"])

with tab_audit:
    # --- ЮРИДИЧЕСКИЙ ДИСКЛЕЙМЕР ---
    st.markdown("""
        <div style="background-color: #ff4b4b22; border: 2px solid #ff4b4b; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="margin-top: 0; color: #ff4b4b;">⚖️ Внимание: Юридический отказ от ответственности</h4>
            <p style="font-size: 0.9em; line-height: 1.4; margin-bottom: 0;">
                Данный сервис работает на базе искусственного интеллекта и <b>не является юридической консультацией</b>. 
                ИИ может ошибаться, галлюцинировать или пропускать важные детали. 
                Результаты анализа носят ознакомительный характер. Перед принятием решений обязательно 
                <b>проконсультируйтесь с квалифицированным юристом</b>. 
                Мы не несем ответственности за последствия использования данного инструмента.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    file = st.file_uploader("Выберите файл договора (PDF)", type=['pdf'], key=f"uploader_{st.session_state.reset_counter}")
    if file:
        if "analysis_result" not in st.session_state:
            if st.button("Начать анализ", use_container_width=True, type="primary"):
                with st.spinner("ИИ проводит глубокий юридический аудит..."):
                    try:
                        with pdfplumber.open(file) as pdf:
                            text = ""
                            for page in pdf.pages:
                                extracted = page.extract_text()
                                if extracted:
                                    text += extracted + "\n"
                        
                        if not text.strip():
                            st.error("❌ Не удалось извлечь текст. Возможно, это изображение или защищенный PDF.")
                            st.stop()
                    except Exception as e:
                        st.error(f"Ошибка при чтении PDF: {e}")
                        st.stop()
                    
                    special_instructions = ""
                    if contract_type == "NDA":
                        special_instructions = "Фокус на сроках конфиденциальности, исключениях и штрафах за разглашение."
                    elif contract_type == "Аренда":
                        special_instructions = "Фокус на индексации цены, условиях расторжения, возврате депозита и текущем ремонте."
                    elif contract_type == "Трудовой":
                        special_instructions = "Фокус на дисциплинарных взысканиях, условиях увольнения, обязанностях и мат. ответственности."
                    elif contract_type == "ИТ-разработка":
                        special_instructions = "Фокус на передаче исключительных прав на код, этапах приемки и гарантийном периоде."
                    elif contract_type == "Поставка / Купля-продажа":
                        special_instructions = "Фокус на переходах рисков, сроках поставки, штрафах за недопоставку и скрытых дефектах."
                    elif contract_type == "Займ":
                        special_instructions = "Фокус на процентах, очередности погашения, штрафах за просрочку и условиях досрочного возврата."
                    elif contract_type == "Лицензионный":
                        special_instructions = "Фокус на территории использования, объеме прав, сублицензировании и роялти."
                    elif contract_type == "Агентский":
                        special_instructions = "Фокус на порядке отчетности агента, расчете вознаграждения и праве на прямой поиск клиентов."

                    prompt_instruction = (
                        "Будь строгим критиком. Если в договоре есть штрафы без вины или односторонние кабальные условия, "
                        "оценка риска (SCORE) должна быть высокой (7-10). "
                        "Разделяй пункты отчета двойным переносом строки для четкой читаемости.\n\n"
                        f"Действуй как опытный корпоративный юрист. Специализация: {contract_type}. "
                        f"Твоя задача — защитить интересы стороны: {user_role}. {special_instructions}\n\n"
                        "ЭТАЛОН КАЧЕСТВА АНАЛИЗА:\n"
                        "🔴 Критический риск: Несоразмерная неустойка (п. 6.2). Установлен штраф 1% в день. "
                        "Юридический анализ: Это 365% годовых, что в 10 раз выше рыночной нормы (0.1%).\n\n"
                        "ИНСТРУКЦИЯ ДВОЙНОЙ ПРОВЕРКИ (Chain of Verification):\n"
                        "Шаг 1: Проанализируй текст и выдели риски.\n"
                        "Шаг 2: Для каждого риска проверь, действительно ли в тексте договора есть указанный пункт и условие.\n"
                        "Шаг 3: Сформируй итоговый отчет. Если риск не подтвержден фактами — удали его.\n\n"
                        "СТРУКТУРА ОТВЕТА (ОБЯЗАТЕЛЬНО):\n"
                        "## ⚖️ Юридический анализ рисков\n"
                        "1. ОБЩИЙ ВЕРДИКТ.\n"
                        "2. ФИНАНСОВЫЕ РИСКИ.\n"
                        "3. РИСКИ РАСТОРЖЕНИЯ И СПОРОВ.\n"
                        "Для каждого риска пиши: 'Суть условия' и 'Юридический анализ'. Используй 🔴, 🟠, 🟡.\n\n"
                        "ТЕХНИЧЕСКАЯ ИНСТРУКЦИЯ: Перед следующим разделом ОБЯЗАТЕЛЬНО напечатай строку [PAYWALL] отдельной строкой.\n\n"
                        "## 🛠️ Протокол разногласий (Готовые правки)\n"
                        "Составь таблицу в формате Markdown для всех найденных рисков:\n"
                        "| № Пункта | Оригинальный текст | Предлагаемая редакция | Обоснование |\n"
                        "| :--- | :--- | :--- | :--- |\n\n"
                        "В самом конце напиши 'SCORE: X' (1-10).\n"
                        "Язык: Русский."
                    )

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": prompt_instruction},
                            {"role": "user", "content": f"Текст договора:\n{text[:10000]}"}
                        ],
                        temperature=0.0
                    )
                    
                    raw_res = response.choices[0].message.content
                    score_match = re.search(r"SCORE:\s*(\d+)", raw_res)
                    score = int(score_match.group(1)) if score_match else 5
                    clean_res = re.sub(r"SCORE:\s*\d+", "", raw_res).strip()

                    if clean_res:
                        try:
                            # --- НОВЫЙ БЛОК ДЛЯ USER_ID ---
                            if st.session_state.user:
                                user_id = st.session_state.user.id
                            else:
                                user_id = None 

                            data = {
                                "contract_type": contract_type, 
                                "raw_analysis": clean_res,
                                "payment_status": "pending",
                                "user_id": user_id # ДОБАВИЛИ ЭТУ СТРОКУ
                            }
                            # ------------------------------
                            insert_result = supabase.table("contract_audits").insert(data).execute()
                            
                            st.session_state.analysis_result = clean_res
                            st.session_state.current_audit_id = insert_result.data[0]['id']
                            st.session_state.audit_score = score
                            
                            st.rerun()
                        except Exception as e:
                            st.error(f"Ошибка при подготовке анализа: {e}")
        else:
            # --- ИНТЕГРИРОВАННЫЙ БЛОК ВЫВОДА ОТЧЕТА ---
            score = st.session_state.get("audit_score", 5)
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

            if "analysis_result" in st.session_state:
                # 1. Возвращаем зеленую плашку успеха
                st.success("✅ Анализ и протокол разногласий успешно сформированы!")

                clean_res = st.session_state.analysis_result
                current_audit_id = st.session_state.current_audit_id

                if "[PAYWALL]" in clean_res:
                    parts = clean_res.split("[PAYWALL]")
                    free_part = parts[0]
                    paid_part = parts[1]

                    # Бесплатная часть
                    st.markdown(f"<div class='report-card'>{free_part.strip()}</div>", unsafe_allow_html=True)
                    st.divider()

                    # Проверка оплаты
                    try:
                        check_db = supabase.table("contract_audits").select("payment_status").eq("id", current_audit_id).single().execute()
                        is_paid = check_db.data.get("payment_status") == "paid"
                    except:
                        is_paid = False

                    if is_paid:
                        st.balloons()
                        st.success("🎉 Оплата подтверждена!")
                        st.markdown(f"<div class='report-card' style='border-left: 5px solid #28a745;'>{paid_part.strip()}</div>", unsafe_allow_html=True)
                        
                        # Ряд кнопок
                        col_pdf, col_sup = st.columns(2)
                        with col_pdf:
                            try:
                                pdf_bytes = create_pdf(clean_res)
                                st.download_button(
                                    label="📥 Скачать отчет (PDF)",
                                    data=bytes(pdf_bytes),
                                    file_name=f"audit_{current_audit_id[:8]}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Ошибка PDF: {e}")
                        
                        with col_sup:
                            st.link_button("🆘 Поддержка", "https://t.me/твой_логин", use_container_width=True)

                        st.write("")
                        if st.button("📁 Загрузить новый договор", use_container_width=True, key="btn_paid_reset"):
                            # Полная очистка
                            st.session_state.reset_counter += 1
                            keys_to_clear = ["analysis_result", "current_audit_id", "audit_score"]
                            for k in keys_to_clear:
                                if k in st.session_state: del st.session_state[k]
                            st.rerun()
                    else:
                        st.warning("🔒 **Полный отчет и Протокол разногласий заблокированы.**")
                        
                        # ДВЕ КНОПКИ В ОДИН РЯД
                        col1, col2 = st.columns(2)
                        with col1:
                            product_id = "a06e3832-bc7a-4d2c-8f1e-113446b2bf61" 
                            payment_url = f"https://jurisclearai.lemonsqueezy.com/checkout/buy/{product_id}?checkout[custom][audit_id]={current_audit_id}"
                            st.link_button("🚀 Оплатить Premium (850 ₽)", payment_url, use_container_width=True)
                        
                        with col2:
                            if st.button("🔄 Проверить оплату", use_container_width=True):
                                st.rerun()
                        
                        st.write("")
                        st.divider()

                        # КНОПКА ОТМЕНЫ (СБРОСА)
                        if st.button("❌ Отменить и загрузить другой файл", use_container_width=True):
                            # Увеличиваем счетчик, чтобы сбросить file_uploader
                            st.session_state.reset_counter += 1
                            # Очищаем данные анализа
                            keys_to_clear = ["analysis_result", "current_audit_id", "audit_score"]
                            for k in keys_to_clear:
                                if k in st.session_state: del st.session_state[k]
                            # Принудительная перезагрузка
                            st.rerun()
                else:
                    # Если PAYWALL нет в тексте
                    st.markdown(f"<div class='report-card'>{clean_res}</div>", unsafe_allow_html=True)
                    
                    # Кнопка скачивания PDF
                    try:
                        pdf_bytes = create_pdf(clean_res)
                        st.download_button(
                            label="📥 Скачать отчет (PDF)",
                            data=bytes(pdf_bytes),
                            file_name=f"audit_{current_audit_id[:8]}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Ошибка PDF: {e}")

                    if st.button("📁 Загрузить новый договор", key="btn_no_paywall_reset", use_container_width=True):
                        st.session_state.reset_counter += 1
                        keys_to_clear = ["analysis_result", "current_audit_id", "audit_score"]
                        for k in keys_to_clear:
                            if k in st.session_state: del st.session_state[k]
                        st.rerun()

    else:
        if "analysis_result" in st.session_state:
            # Очистка если файл убран из uploader вручную
            keys_to_clear = ["analysis_result", "current_audit_id", "audit_score"]
            for k in keys_to_clear:
                if k in st.session_state: del st.session_state[k]
        st.info("Пожалуйста, загрузите файл договора в формате PDF для начала анализа.")

with tab_demo:
    st.write("### Так выглядит результат анализа:")
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

with tab_history:
    st.subheader("📜 История ваших аудитов")
    
    if st.session_state.user is None:
        st.warning("Пожалуйста, войдите в аккаунт, чтобы просмотреть историю своих анализов.")
    else:
        try:
            # Запрашиваем из базы все анализы текущего пользователя
            history = supabase.table("contract_audits") \
                .select("*") \
                .eq("user_id", st.session_state.user.id) \
                .order("created_at", ascending=False) \
                .execute()
            
            if not history.data:
                st.info("У вас пока нет сохраненных анализов.")
            else:
                for audit in history.data:
                    # Создаем аккуратную карточку для каждого старого анализа
                    date_str = audit['created_at'][:10] # Берем только дату
                    status = "✅ Оплачено" if audit['payment_status'] == 'paid' else "⏳ Ожидает оплаты"
                    
                    with st.expander(f"📄 {audit['contract_type']} от {date_str} — {status}"):
                        # Показываем результат (если оплачено — весь, если нет — только начало)
                        res_text = audit['raw_analysis']
                        if "[PAYWALL]" in res_text and audit['payment_status'] != 'paid':
                            st.markdown(res_text.split("[PAYWALL]")[0])
                            st.warning("Этот отчет не оплачен. Оплатите его в основной вкладке, чтобы открыть полный доступ.")
                        else:
                            st.markdown(res_text.replace("[PAYWALL]", ""))
                            
                            # Кнопка скачивания PDF в истории (только если оплачено)
                            try:
                                pdf_bytes = create_pdf(res_text)
                                st.download_button(
                                    label="📥 Скачать PDF",
                                    data=bytes(pdf_bytes),
                                    file_name=f"audit_{date_str}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_{audit['id']}"
                                )
                            except Exception as e:
                                st.error(f"Ошибка PDF: {e}")
                            
        except Exception as e:
            st.error(f"Не удалось загрузить историю: {e}")

st.divider()
st.caption("© 2026 JurisClear AI | Ереван, Армения | support@jurisclear.com")
