import streamlit as st # UI Updated: Elite Premium Polish (Tactile & Glow)
from openai import OpenAI
import re
from supabase import create_client, Client  # Добавили импорт Supabase

# Импорты из локальных модулей
from ui.design import load_css, get_risk_params, sample_text
from utils.file_processing import extract_text_from_pdf
from core.intelligence import analyze_long_text, generate_analysis
from utils.export import create_pdf, create_docx

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="JurisClear AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ИНИЦИАЛИЗАЦИЯ ---
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

# Загружаем дизайн
load_css()

# --- 3. ИНИЦИАЛИЗАЦИЯ AUTH STATE ---
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

@st.dialog("JurisClear AI")
def show_auth_modal():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h3 style='margin-bottom: 5px;'>Добро пожаловать</h3>
            <p style='color: var(--secondary-text); font-size: 14px;'>Войдите в систему для доступа к Pro функциям</p>
        </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["🔐 Вход", "📝 Регистрация"])
    
    with tabs[0]:
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        email = st.text_input("Электронная почта", placeholder="example@mail.com", key="login_email")
        password = st.text_input("Пароль", type="password", placeholder="••••••••", key="login_pass")
        
        st.markdown("""
            <div style='display: flex; justify-content: flex-end; margin-bottom: 15px;'>
                <a href='#' style='font-size: 12px; color: var(--accent-blue); text-decoration: none; opacity: 0.8;'>Забыли пароль?</a>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Войти", use_container_width=True, type="primary"):
            # Имитация входа для демонстрации UI
            st.session_state.is_authenticated = True
            st.session_state.user_email = email if email else "user@example.com"
            st.rerun()

    with tabs[1]:
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        reg_name = st.text_input("Имя", placeholder="Иван Иванов", key="reg_name")
        reg_email = st.text_input("Электронная почта", placeholder="example@mail.com", key="reg_email")
        reg_password = st.text_input("Пароль", type="password", placeholder="••••••••", key="reg_pass")
        
        if st.button("Создать аккаунт", use_container_width=True, type="primary"):
            st.toast("Функционал регистрации будет доступен скоро! ✨", icon="⚙️")

    st.markdown("""
        <div class="auth-footer">
            Продолжая, вы соглашаетесь с нашими <br> 
            <a href='#' style='color: var(--accent-blue);'>Условиями использования</a>
        </div>
    """, unsafe_allow_html=True)

# --- 4. ПОДКЛЮЧЕНИЕ API И БАЗЫ ДАННЫХ ---
# OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Supabase
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets.get("SUPABASE_SERVICE_KEY") or st.secrets.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Ошибка подключения к Supabase: {e}. Проверьте secrets.toml")
    supabase = None

# --- 5. ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---

# --- ХЕДЕР ПРИЛОЖЕНИЯ ---
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 40px; line-height: 1;">⚖️</span>
            <div style="display: flex; flex-direction: column;">
                <h1 style='color: var(--header-color); margin: 0; padding: 0; font-size: 32px; font-weight: 800; line-height: 1;'>JurisClear <span style='color:var(--accent-blue)'>AI</span></h1>
            </div>
        </div>
    """, unsafe_allow_html=True)

with header_col2:
    if not st.session_state.is_authenticated:
        st.markdown('<div class="login-btn-header">', unsafe_allow_html=True)
        if st.button("Войти 👤", use_container_width=True):
            show_auth_modal()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Имитация профиля пользователя
        cols = st.columns([1, 1.5])
        with cols[0]:
            st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: flex-end; height: 100%; margin-top: 5px;">
                    <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3); border: 1px solid rgba(255,255,255,0.2);">
                        {st.session_state.user_email[0].upper() if st.session_state.user_email else "U"}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            if st.button("Выйти", use_container_width=True):
                st.session_state.is_authenticated = False
                st.rerun()

st.markdown(f"<p style='text-align: center; color: var(--secondary-text); font-weight: 500;'>Профессиональный юридический аудит договоров</p>", unsafe_allow_html=True)

# --- ОБНОВЛЕННЫЕ ТАРИФЫ (SOFT UI) ---
col_tar1, col_tar2 = st.columns(2)

with col_tar1:
    st.markdown(f"""
        <div class="pricing-card-base pricing-card-1">
            <div>
                <div style="font-size: 20px; font-weight: 600; opacity: 0.9;">Разовый аудит</div>
                <div style="font-size: 32px; font-weight: 800; margin: 10px 0;">9 $</div>
                <div style="font-size: 13px; opacity: 0.8; line-height: 1.6;">
                    • <b>Бесплатное резюме</b> основных рисков<br>
                    • Детальный юридический разбор (Full Report)<br>
                    • Конкретные правки для защиты ваших интересов<br>
                    • Экспорт отчета в PDF и Word<br>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div style="background: rgba(0,0,0,0.05); padding: 10px; border-radius: 10px; text-align: center; font-size: 13px; font-weight: 500;">
                    ℹ️ Оплачивайте только если результат вас устроит
                </div>
                <div style="width: 100%; background: rgba(99, 102, 241, 0.1); color: var(--accent-blue); border: 1px solid rgba(99, 102, 241, 0.2); padding: 12px; border-radius: 10px; font-weight: 600; text-align: center; cursor: default;">Анализ доступен ниже 👇</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_tar2:
    st.markdown(f"""
        <div class="pricing-card-base pricing-card-2">
            <div>
                <div style="font-size: 20px; font-weight: 600; opacity: 0.9;">Безлимит Pro</div>
                <div style="font-size: 32px; font-weight: 800; margin: 10px 0;">29 $ <span style="font-size: 14px; opacity: 0.7;">/мес</span></div>
                <div style="font-size: 13px; opacity: 0.8; line-height: 1.6;">
                    • <b>Неограниченное</b> количество документов<br>
                    • Полные отчеты <b>мгновенно</b> без доплат<br>
                    • Доступ к результату в истории навсегда<br>
                    • Персональный архив всех проверок<br>
                    • Самая мощная модель ИИ (GPT-4o)
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div style="background: rgba(99, 102, 241, 0.1); padding: 10px; border-radius: 10px; text-align: center; font-size: 13px; font-weight: 500; color: var(--accent-blue);">
                    🔐 Для оформления подписки нужно зарегистрироваться
                </div>
                <div style="background: rgba(255,255,255,0.05); color: var(--secondary-text); text-align: center; padding: 12px; border-radius: 10px; font-weight: 700; font-size: 15px; border: 1px dashed var(--border-color); cursor: not-allowed;">
                    🚀 Оформить подписку
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Параметры анализа
with st.container():
    st.markdown("""
        <div id="analysis-params-hook" style='display: flex; align-items: center; gap: 15px; margin-bottom: 25px;'>
            <div style='background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4); border: 1px solid rgba(255,255,255,0.1);'>⚙️</div>
            <h2 style='margin: 0; font-size: 26px; font-weight: 800; color: var(--header-color); letter-spacing: -0.5px;'>Параметры анализа</h2>
        </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<p style='font-size: 13px; font-weight: 700; color: var(--secondary-text); text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 10px;'>Ваша роль</p>", unsafe_allow_html=True)
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
            label_visibility="collapsed",
            key=f"role_pills_{st.session_state.reset_counter}"
        )

    with c2:
        st.markdown("<p style='font-size: 13px; font-weight: 700; color: var(--secondary-text); text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 10px;'>Тип документа</p>", unsafe_allow_html=True)
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
            label_visibility="collapsed",
            key=f"type_pills_{st.session_state.reset_counter}"
        )

# Рабочее пространство (Вкладки)
tab_audit, tab_demo = st.tabs(["🚀 ИИ Аудит", "📝 Пример отчета"])

with tab_audit:
    # --- ЮРИДИЧЕСКИЙ ДИСКЛЕЙМЕР ---
    st.markdown("""
        <div class="legal-disclaimer" style="display: block !important;">
            <h4 style="color: #ef4444 !important;">⚖️ Внимание: Юридический отказ от ответственности</h4>
            <p style="font-size: 0.9em; line-height: 1.5; margin-bottom: 0; color: var(--text-color); opacity: 0.9;">
                Данный сервис работает на базе искусственного интеллекта и <b>не является юридической консультацией</b>. 
                ИИ может ошибаться или пропускать важные детали. 
                Результаты анализа носят ознакомительный характер. Перед принятием решений обязательно 
                <b>проконсультируйтесь с квалифицированным юристом</b>. 
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    file = st.file_uploader("Выберите файл договора (PDF)", type=['pdf'], key=f"uploader_{st.session_state.reset_counter}")
    
    # --- СБРОС ПАМЯТИ ---
    # Если файл не загружен (или удален крестиком), очищаем результаты старого анализа
    if file is None:
        if "analysis_result" in st.session_state:
            del st.session_state["analysis_result"]
        if "audit_score" in st.session_state:
            del st.session_state["audit_score"]
            
    if file:
        if "analysis_result" not in st.session_state:
            if st.button("Начать анализ", use_container_width=True, type="primary"):
                with st.spinner("ИИ проводит глубокий юридический аудит..."):
                    try:
                        # --- ИНТЕГРИРОВАННЫЙ КУСОЧЕК КОДА ---
                        file_bytes = file.read() # Считываем байты один раз
                        text = extract_text_from_pdf(file_bytes)

                        if not text.strip():
                            st.error("Не удалось извлечь текст из документа. Возможно, файл поврежден или пуст.")
                            st.stop()
                        # -----------------------------------
                        
                    except Exception as e:
                        st.error(f"Ошибка при чтении PDF: {e}")
                        st.stop()
                    
                    special_instructions = ""
                    if contract_type == "NDA":
                        special_instructions = "Фокус на сроках конфиденциальности, исключениях и штрафaх за разглашение."
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
                        special_instructions = "Фокус на порядке отчетности агента, расчете вознаграждеия и праве на прямой поиск клиентов."

                    prompt_instruction = (
                        "СТРУКТУРА ОТВЕТА (ОБЯЗАТЕЛЬНО):\n"
                        "## ⚖️ Юридический анализ рисков\n"
                        "1. ОБЩИЙ ВЕРДИКТ.\n"
                        "2. ФИНАНСОВЫЕ РИСКИ.\n"
                        "3. РИСКИ РАСТОРЖЕНИЯ И СПОРОВ.\n"
                        "Для каждого риска пиши: 'Суть условия' и 'Юридический анализ'. Используй 🔴, 🟠, 🟡.\n\n"
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
                        " ## 🛠️ Протокол разногласий (Готовые правки)\n"
                        "Составь таблицу в формате Markdown для всех найденных рисков:\n"
                        "| № Пункта | Оригинальный текст | Предлагаемая редакция | Обоснование |\n"
                        "| :--- | :--- | :--- | :--- |\n\n"
                        "В самом конце напиши 'SCORE: X' (1-10).\n"
                        "Язык: Русский."
                    )

                    # Используем функцию для анализа длинного текста
                    raw_res = analyze_long_text(client, text, contract_type, user_role, special_instructions, prompt_instruction)
                    
                    # Извлекаем оценку и очищаем текст для интерфейса
                    score_match = re.search(r"SCORE:\s*(\d+)", raw_res)
                    score = int(score_match.group(1)) if score_match else 5
                    clean_res = re.sub(r"SCORE:\s*\d+", "", raw_res).strip()

                    if clean_res:
                        st.session_state.analysis_result = clean_res
                        st.session_state.audit_score = score
                        st.rerun()
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
                st.success("✅ Анализ и протокол разногласий успешно сформированы!")

                clean_res = st.session_state.analysis_result
                
                # Показываем результат сразу
                st.markdown(f"<div class='report-card'>{clean_res.strip()}</div>", unsafe_allow_html=True)
                
                # Явный отступ
                st.write("")
                st.write("")
                
                # Две колонки для кнопок скачивания
                col_pdf, col_word = st.columns(2)
                
                with col_pdf:
                    pdf_bytes = create_pdf(clean_res)
                    if pdf_bytes:
                        st.download_button(
                            label="📥 Скачать PDF",
                            data=bytes(pdf_bytes),
                            file_name=f"audit_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                
                with col_word:
                    try:
                        word_bytes = create_docx(clean_res)
                        if word_bytes:
                            st.download_button(
                                label="📝 Скачать Word",
                                data=word_bytes,
                                file_name=f"audit_report.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                    except Exception as e:
                        pass

                st.write("")
                if st.button("📁 Загрузить новый договор", use_container_width=True, key="btn_paid_reset"):
                    st.session_state.reset_counter += 1
                    keys_to_clear = ["analysis_result", "audit_score"]
                    for k in keys_to_clear:
                        if k in st.session_state: del st.session_state[k]
                    st.rerun()
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

st.divider()
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption("© 2026 JurisClear AI | Ереван")

st.markdown(f"<p style='text-align: center; color: var(--secondary-text); font-size: 12px; margin-top: 40px; opacity: 0.6;'>support@jurisclear.com</p>", unsafe_allow_html=True)
