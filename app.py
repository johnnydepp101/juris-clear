import streamlit as st
from openai import OpenAI
import pdfplumber
import re
from supabase import create_client, Client  # Добавили импорт Supabase
import os
from fpdf import FPDF
from docx import Document
from io import BytesIO
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

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
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 2. ВЕСЬ ДИЗАЙН (ПРЕМИАЛЬНЫЙ АДАПТИВНЫЙ CSS) ---
st.markdown("""
    <style>
    /* 1. ПЕРЕМЕННЫЕ ПО УМОЛЧАНИЮ (DARK THEME) */
    :root {
        --bg-color: #0d1117;
        --card-bg: rgba(30, 41, 59, 0.7);
        --text-color: #f0f6fc;
        --secondary-text: #8b949e;
        --border-color: rgba(255, 255, 255, 0.1);
        --accent-blue: #3b82f6;
        --accent-green: #10b981;
        --glass-blur: blur(10px);
        --card-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        --header-color: #ffffff;
    }

    /* 2. АВТОМАТИЧЕСКАЯ СВЕТЛАЯ ТЕМА (ПО НАСТРОЙКАМ СИСТЕМЫ) */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-color: #f8fafc;
            --card-bg: rgba(255, 255, 255, 0.8);
            --text-color: #1e293b;
            --secondary-text: #64748b;
            --border-color: rgba(0, 0, 0, 0.1);
            --card-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            --header-color: #0f172a;
        }
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    .block-container {
        padding-top: 2rem; 
        max-width: 1000px;
    }
    
    /* ГЛОБАЛЬНЫЕ СТИЛИ */
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-color);
        color: var(--text-color);
        transition: all 0.4s ease;
    }

    /* УБИРАЕМ ЯКОРЯ */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, 
    .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a { display: none !important; }
    [data-testid="stMarkdownHeader"] a { display: none !important; }

    /* ХЕДЕР И ВЫРАВНИВАНИЕ */
    [data-testid="stHorizontalBlock"] { align-items: center !important; }

    /* ПРЕМИАЛЬНЫЕ ТАРИФНЫЕ КАРТОЧКИ (GLASSMORPHISM) */
    .pricing-card-single {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(59, 130, 246, 0.8) 100%);
        backdrop-filter: var(--glass-blur);
        padding: 25px; border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.2); 
        text-align: center; color: white;
        box-shadow: var(--card-shadow);
        transition: transform 0.3s ease;
    }
    .pricing-card-pro {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.9) 0%, rgba(16, 185, 129, 0.8) 100%);
        backdrop-filter: var(--glass-blur);
        padding: 25px; border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.2); 
        text-align: center; color: white;
        box-shadow: var(--card-shadow);
        transition: transform 0.3s ease;
    }
    .pricing-card-single:hover, .pricing-card-pro:hover {
        transform: translateY(-5px);
    }
    
    /* КАРТОЧКА ОТЧЕТА */
    .report-card {
        background-color: var(--card-bg);
        backdrop-filter: var(--glass-blur);
        border-left: 6px solid var(--accent-blue);
        padding: 30px; border-radius: 16px; 
        margin-top: 25px; color: var(--text-color);
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
        box-shadow: var(--card-shadow);
    }
    
    /* ШКАЛА РИСКА */
    .risk-meter-container {
        background: rgba(0, 0, 0, 0.2); 
        border-radius: 20px; padding: 10px;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.3); 
        border: 1px solid var(--border-color); 
        margin: 20px 0;
    }
    
    /* КНОПКИ */
    .stButton > button, .stLinkButton > a, .stDownloadButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        font-size: 14px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
    }

    .stButton > button:hover {
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        transform: scale(1.02);
    }

    .stLinkButton > a {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
    }

    .stDownloadButton > button {
        background: var(--border-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* МАЛЕНЬКИЕ УЛУЧШЕНИЯ ТИПОГРАФИКИ */
    .secondary-text {
        color: var(--secondary-text);
        font-size: 0.9rem;
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
# Попытка инициализации из секретов Streamlit (рекомендуемый способ)
try:
    url: str = st.secrets["SUPABASE_URL"]
    # Пробуем взять Service Key для полной свободы действий, если он есть, иначе Anon Key
    key: str = st.secrets.get("SUPABASE_SERVICE_KEY") or st.secrets.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    # Auth-клиент (anon key) — для регистрации/входа (service key НЕ подходит для auth)
    supabase_auth: Client = create_client(url, st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error(f"Ошибка подключения к Supabase: {e}. Проверьте secrets.toml")
    # Создаем фиктивный клиент, чтобы приложение не вылетало сразу при отрисовке UI
    supabase = None
    supabase_auth = None

# --- ФУНКЦИЯ ИЗВЛЕЧЕНИЯ ТЕКСТА (ОБНОВЛЕННАЯ С ГИБРИДНЫМ OCR) ---
def extract_text_from_pdf(file_bytes):
    """
    Гибридная функция: сначала пробует вытащить текст напрямую, 
    если не выходит — использует OCR (Tesseract).
    """
    text = ""
    # 1. Пробуем стандартный метод (pdfplumber)
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception as e:
        st.warning(f"Обычное чтение PDF не удалось, пробуем OCR... ({e})")

    # 2. Если текста почти нет (< 100 символов), значит это скан или фото
    if len(text.strip()) < 100:
        with st.status("🔍 Обнаружен скан. Работает OCR (распознавание текста)...", expanded=True) as status:
            try:
                # Конвертируем PDF в список изображений (каждая страница = картинка)
                images = convert_from_bytes(file_bytes)
                
                ocr_text = ""
                total_pages = len(images)
                
                for i, image in enumerate(images):
                    st.write(f"Обработка страницы {i+1} из {total_pages}...")
                    # Распознаем текст (русский + английский)
                    page_text = pytesseract.image_to_string(image, lang='rus+eng')
                    ocr_text += f"\n--- Страница {i+1} ---\n" + page_text
                
                status.update(label="✅ Распознавание завершено!", state="complete", expanded=False)
                return ocr_text
            except Exception as e:
                st.error(f"Ошибка OCR: {e}. Убедитесь, что tesseract-ocr прописан в packages.txt")
                return ""
    
    return text

# --- ФУНКЦИЯ СОЗДАНИЯ PDF (ИНТЕГРИРОВАНА НОВАЯ ПРОВЕРКА ШРИФТА) ---
def create_pdf(text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15) # Авто-перенос страниц
    pdf.add_page()
    
    # Путь к шрифту
    font_path = "DejaVuSans.ttf" 
    
    # Новая логика проверки шрифта
    if not os.path.exists(font_path):
        st.error("Критическая ошибка: Файл шрифта DejaVuSans.ttf не найден. PDF не может быть создан.")
        return None
        
    pdf.add_font('DejaVu', '', font_path)
    pdf.set_font('DejaVu', '', 12)
    
    # Используем write вместо multi_cell. 
    # 10 — это высота строки. write() сам переносит текст и слова.
    pdf.write(10, text.strip())
    
    return pdf.output()

# --- ФУНКЦИЯ СОЗДАНИЯ WORD ---
def create_docx(text):
    doc = Document()
    doc.add_heading('Результат анализа договора - JurisClear AI', 0)
    
    # Разбиваем текст на параграфы для красоты
    for paragraph in text.strip().split('\n'):
        if paragraph.strip():
            doc.add_paragraph(paragraph)
    
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- ФУНКЦИЯ ДЛЯ АНАЛИЗА ДЛИННЫХ ТЕКСТОВ ---
def analyze_long_text(full_text, contract_type, user_role, special_instructions, prompt_instruction):
    # Делим текст по абзацам, а не по символам
    paragraphs = full_text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < 15000:
            current_chunk += p + "\n\n"
        else:
            chunks.append(current_chunk)
            current_chunk = p + "\n\n"
    if current_chunk:
        chunks.append(current_chunk)
    
    partial_analyses = []
    
    # Индикатор прогресса для пользователя
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, chunk in enumerate(chunks):
        status_text.text(f"Анализирую часть {idx+1} из {len(chunks)}...")
        
        prompt = (
            f"Ты — опытный юрист. Проанализируй эту ЧАСТЬ договора ({idx+1}/{len(chunks)}). "
            f"Тип: {contract_type}, Роль: {user_role}. {special_instructions}\n\n"
            "Выдели только КРИТИЧЕСКИЕ риски и кабальные условия, которые видишь в этом куске.\n"
            f"Текст части:\n{chunk}"
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Используем mini для промежуточных частей (быстрее и дешевле)
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        partial_analyses.append(response.choices[0].message.content)
        progress_bar.progress((idx + 1) / len(chunks))

    # 2. Финальная сборка отчета
    status_text.text("Формирую итоговый отчет и протокол разногласий...")
    
    combined_context = "\n\n".join(partial_analyses)
    
    final_prompt = (
        "Перед тобой промежуточные результаты анализа разных частей одного договора. "
        "Твоя задача — объединить их в один профессиональный, структурированный отчет.\n\n"
        "УДАЛИ повторы. СГРУППИРУЙ риски по категориям (Финансовые, Сроки, Ответственность).\n"
        "СОСТАВЬ итоговую таблицу 'Протокол разногласий'.\n\n"
        "СТРУКТУРА И ЯЗЫК ОТВЕТА ДОЛЖНЫ СТРОГО СООТВЕТСТВОВАТЬ ЭТАЛОНУ (с SCORE).\n\n"
        f"Промежуточные данные:\n{combined_context}"
    )
    
    final_response = client.chat.completions.create(
        model="gpt-4o", # Для финала используем мощную модель
        messages=[
            {"role": "system", "content": prompt_instruction}, # Используем твой основной системный промпт
            {"role": "user", "content": final_prompt}
        ],
        temperature=0.0
    )
    
    status_text.empty()
    progress_bar.empty()
    
    return final_response.choices[0].message.content

# --- НОВАЯ ФУНКЦИЯ АНАЛИЗА (INTEGRATED) ---
def generate_analysis(full_text, contract_type, user_role, special_reqs):

    # --- НАСТРОЙКИ ЧАНКИНГА ---
    MAX_CHUNK_SIZE = 15000  # Примерно 3000-4000 токенов

    # 1. Если текст короткий, анализируем в один проход
    if len(full_text) < MAX_CHUNK_SIZE:
        prompt = f"""
        Ты — профессиональный корпоративный юрист. Проведи полный аудит договора: {contract_type}.
        Моя роль: {user_role}. Особые требования: {special_reqs if special_reqs else 'Нет'}.
        Текст договора:
        {full_text}
        
        Выдай отчет в Markdown: Резюме, Риски (Критический/Средний/Низкий), Топ-3 опасных пункта, Рекомендации.
        """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content

    # 2. Если текст длинный — включаем логику ЧАНКИНГА
    st.info(f"⏳ Договор очень длинный ({len(full_text)} симв.). Анализирую по частям...")
    
    paragraphs = full_text.split('\n\n')
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < MAX_CHUNK_SIZE:
            current_chunk += p + "\n\n"
        else:
            chunks.append(current_chunk)
            current_chunk = p + "\n\n"
    if current_chunk:
        chunks.append(current_chunk)

    # Собираем риски из каждой части
    partial_risks = []
    progress_bar = st.progress(0)
    
    for i, chunk in enumerate(chunks):
        st.write(f"Сканирую часть {i+1} из {len(chunks)}...")
        chunk_prompt = f"Найди все юридические риски в этой части договора {contract_type} для роли {user_role}. Текст:\n{chunk}"
        
        chunk_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": chunk_prompt}],
            temperature=0
        )
        partial_risks.append(chunk_res.choices[0].message.content)
        progress_bar.progress((i + 1) / len(chunks))

    # --- ФИНАЛЬНЫЙ СИНТЕЗ ---
    st.write("Сборка финального отчета...")
    all_risks_text = "\n\n".join(partial_risks)
    
    final_prompt = f"""
    Ты — старший юрист. Перед тобой список рисков, найденных в разных частях одного договора ({contract_type}).
    Твоя задача: объединить их в один логичный, структурированный отчет для клиента ({user_role}).
    Исключи повторы и выдели самые критические моменты.
    
    Список всех найденных рисков:
    {all_risks_text}
    
    Выдай финальный отчет в Markdown: Резюме, Общая оценка рисков, Детальный список ловушек, Рекомендации.
    """
    
    final_res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.2
    )
    return final_res.choices[0].message.content

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

# --- 5. АВТОРИЗАЦИЯ (ОПЦИОНАЛЬНАЯ, В САЙДБАРЕ) ---
def show_auth_sidebar():
    """Формы входа/регистрации в боковой панели."""
    with st.sidebar:
        st.markdown("### 🔐 Личный кабинет")
        
        if st.session_state.user:
            # Пользователь уже вошел
            user_email = st.session_state.user.email
            st.markdown(f"""
                <div style="background: var(--card-bg); backdrop-filter: var(--glass-blur); 
                     border-radius: 16px; padding: 20px; border: 1px solid var(--border-color);
                     margin-bottom: 15px;">
                    <p style="margin: 0 0 5px 0; font-size: 13px; color: var(--secondary-text);">Вы вошли как:</p>
                    <p style="margin: 0; font-weight: 700; color: var(--text-color); font-size: 15px;">👤 {user_email}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Выйти из аккаунта", use_container_width=True, key="sidebar_logout"):
                try:
                    supabase_auth.auth.sign_out()
                except Exception:
                    pass
                st.session_state.user = None
                keys_to_clear = ["analysis_result", "audit_score"]
                for k in keys_to_clear:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
        else:
            # Пользователь не вошел — показываем формы
            tab_login, tab_register = st.tabs(["🔑 Вход", "📝 Регистрация"])

            with tab_login:
                with st.form("login_form", clear_on_submit=False):
                    email = st.text_input("Email", placeholder="name@example.com", key="login_email")
                    password = st.text_input("Пароль", type="password", placeholder="Минимум 6 символов", key="login_password")
                    submit = st.form_submit_button("Войти", use_container_width=True, type="primary")

                    if submit:
                        if not email or not password:
                            st.error("Заполните все поля")
                        else:
                            try:
                                data = supabase_auth.auth.sign_in_with_password({
                                    "email": email,
                                    "password": password
                                })
                                st.session_state.user = data.user
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "Invalid login credentials" in error_msg:
                                    st.error("❌ Неверный email или пароль")
                                elif "Email not confirmed" in error_msg:
                                    st.error("📧 Email не подтвержден. Проверьте почту.")
                                else:
                                    st.error(f"Ошибка входа: {error_msg}")

            with tab_register:
                with st.form("register_form", clear_on_submit=False):
                    new_email = st.text_input("Email", placeholder="name@example.com", key="reg_email")
                    new_password = st.text_input("Пароль", type="password", placeholder="Минимум 6 символов", key="reg_password")
                    new_password2 = st.text_input("Повторите пароль", type="password", placeholder="Минимум 6 символов", key="reg_password2")
                    submit_reg = st.form_submit_button("Создать аккаунт", use_container_width=True, type="primary")

                    if submit_reg:
                        if not new_email or not new_password or not new_password2:
                            st.error("Заполните все поля")
                        elif new_password != new_password2:
                            st.error("❌ Пароли не совпадают")
                        elif len(new_password) < 6:
                            st.error("❌ Пароль должен быть не менее 6 символов")
                        else:
                            try:
                                data = supabase_auth.auth.sign_up({
                                    "email": new_email,
                                    "password": new_password
                                })
                                # Проверка: если email confirmation отключена, user сразу авторизован
                                if data.user and data.user.aud == "authenticated":
                                    st.session_state.user = data.user
                                    st.success("✅ Регистрация прошла успешно!")
                                    st.rerun()
                                else:
                                    st.success("✅ Аккаунт создан! Проверьте почту для подтверждения.")
                            except Exception as e:
                                error_msg = str(e)
                                if "User already registered" in error_msg:
                                    st.error("❌ Пользователь с таким email уже существует")
                                elif "rate limit" in error_msg.lower():
                                    st.error("⏳ Слишком много попыток. Подождите минуту.")
                                else:
                                    st.error(f"Ошибка регистрации: {error_msg}")

            st.markdown("<p style='text-align: center; color: var(--secondary-text); font-size: 0.8rem; margin-top: 15px;'>🔒 Данные защищены шифрованием Supabase</p>", unsafe_allow_html=True)

# Вызываем сайдбар авторизации
show_auth_sidebar()

# --- 6. ИНТЕРФЕЙС ПРИЛОЖЕНИЯ (доступен всем) ---

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
    if st.session_state.user:
        user_email = st.session_state.user.email
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; height: 100%;">
                <span style="color: var(--secondary-text); font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px;" title="{user_email}">
                    👤 {user_email}
                </span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.write("") # Место для будущего профиля

st.markdown(f"<p style='text-align: center; color: var(--secondary-text); font-weight: 500;'>Профессиональный юридический аудит договоров</p>", unsafe_allow_html=True)

# --- ОБНОВЛЕННЫЕ ТАРИФЫ С КОНКРЕТНЫМИ ФУНКЦИЯМИ ---
col_tar1, col_tar2 = st.columns(2)

card_style = """
    display: flex; 
    flex-direction: column; 
    justify-content: space-between; 
    padding: 25px; 
    border-radius: 15px; 
    height: 420px; 
    color: white;
"""

with col_tar1:
    st.markdown(f"""
        <div style="{card_style} background: linear-gradient(135deg, #1e293b 0%, #3b82f6 100%); border: 1px solid #3b82f6;">
            <div>
                <div style="font-size: 20px; font-weight: 600; opacity: 0.9;">Разовый аудит</div>
                <div style="font-size: 32px; font-weight: 800; margin: 10px 0;">850 ₽</div>
                <div style="font-size: 13px; opacity: 0.8; line-height: 1.6;">
                    • <b>Бесплатное резюме</b> основных рисков<br>
                    • Детальный юридический разбор (Full Report)<br>
                    • Конкретные правки для защиты ваших интересов<br>
                    • Экспорт отчета в PDF и Word<br>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div style="background: rgba(0,0,0,0.2); padding: 8px; border-radius: 8px; text-align: center; font-size: 11px;">
                    ℹ️ Оплачивайте только если результат вас устроит
                </div>
                <button style="width: 100%; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.3); padding: 12px; border-radius: 10px; font-weight: 600; cursor: default;">Анализ доступен ниже 👇</button>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_tar2:
    checkout_url = "https://jurisclearai.lemonsqueezy.com/checkout/buy/69a180c9-d5f5-4018-9dbe-b8ac64e4ced8"
    st.markdown(f"""
        <div style="{card_style} background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); border: 1px solid #60a5fa; box-shadow: 0 10px 25px rgba(59,130,246,0.3);">
            <div>
                <div style="font-size: 20px; font-weight: 600; opacity: 0.9;">Безлимит Pro</div>
                <div style="font-size: 32px; font-weight: 800; margin: 10px 0;">2500 ₽ <span style="font-size: 14px; opacity: 0.7;">/мес</span></div>
                <div style="font-size: 13px; opacity: 0.8; line-height: 1.6;">
                    • <b>Неограниченное</b> количество документов<br>
                    • Полные отчеты <b>мгновенно</b> без доплат<br>
                    • Доступ к результату в истории навсегда<br>
                    • Персональный архив всех проверок<br>
                    • Самая мощная модель ИИ (GPT-4o)
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div style="height: 33px;"></div> <!-- Spacer for alignment -->
                <a href="{checkout_url}" target="_blank" style="display: block; background: white; color: #1d4ed8; text-align: center; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 15px;">🚀 Оформить подписку</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

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
        label_visibility="collapsed",
        key=f"role_pills_{st.session_state.reset_counter}"
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
        label_visibility="collapsed",
        key=f"type_pills_{st.session_state.reset_counter}"
    )

# Рабочее пространство (Вкладки)
tab_audit, tab_redline, tab_demo = st.tabs(["🚀 ИИ Аудит", "🔄 Сравнение версий", "📝 Пример отчета"])

with tab_audit:
    # --- ЮРИДИЧЕСКИЙ ДИСКЛЕЙМЕР ---
    st.markdown("""
        <div style="background-color: #ff4b4b22; border: 2px solid #ff4b4b; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="margin-top: 0; color: #ff4b4b;">⚖️ Внимание: Юридический отказ от ответственности</h4>
            <p style="font-size: 0.9em; line-height: 1.4; margin-bottom: 0;">
                Данный сервис работает на базе искусственного интеллекта и <b>не является юридической консультацией</b>. 
                ИИ может ошибаться, галлюцинировать или пропускать важные детали. 
                Результаты анализа носят ознакоительный характер. Перед принятием решений обязательно 
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
                    raw_res = analyze_long_text(text, contract_type, user_role, special_instructions, prompt_instruction)
                    
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
                
                # Три колонки для кнопок (ID заменен на фейковый или удален)
                col_pdf, col_word, col_sup = st.columns(3)
                
                with col_pdf:
                    pdf_bytes = create_pdf(clean_res)
                    if pdf_bytes:
                        st.download_button(
                            label="📥 PDF",
                            data=bytes(pdf_bytes),
                            file_name=f"audit_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.warning("PDF не доступен")
                
                with col_word:
                    try:
                        word_bytes = create_docx(clean_res)
                        if word_bytes:
                            st.download_button(
                                label="📝 Word",
                                data=word_bytes,
                                file_name=f"audit_report.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                        else:
                            st.warning("Word не доступен")
                    except Exception as e:
                        st.error("Ошибка Word")
                
                with col_sup:
                    st.link_button("🆘 Поддержка", "https://t.me/твой_логин", use_container_width=True)

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
with col_f2:
    if st.button("Конфиденциальность", type="tertiary"):
        st.info("Политика конфиденциальности...")
with col_f3:
    if st.button("Условия", type="tertiary"):
        st.info("Условия использования...")

st.markdown(f"<p style='text-align: center; color: var(--secondary-text); font-size: 11px; margin-top: 20px;'>support@jurisclear.com</p>", unsafe_allow_html=True)
