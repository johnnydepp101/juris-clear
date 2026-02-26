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
    /* Ультимативное выравнивание ВСЕХ кнопок: Обычных, Ссылок и Скачивания */
    .stButton > button, .stLinkButton > a, .stDownloadButton > button {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 50px !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 10px 20px !important;
        border-radius: 10px !important;
        text-decoration: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* Цвет для кнопки скачивания (сделаем её чуть отличной, например, серой или оставить синей) */
    .stDownloadButton > button {
        background-color: #1e293b !important; /* Темно-синий/серый */
        color: white !important;
    }
    .stDownloadButton > button:hover {
        background-color: #334155 !important;
        border-color: #3b82f6 !important;
    }
    
    /* Цвет для кнопки Оплатить (Primary) */
    .stLinkButton > a {
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
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
# Используем Service Role Key, чтобы обойти проблемы с JWT в Streamlit
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# Функция для выхода
def sign_out():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

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
    
    # Новая логика проверки из запроса
    if not os.path.exists(font_path):
        raise FileNotFoundError("Критическая ошибка: Шрифт для PDF не найден!")
        
    pdf.add_font('DejaVu', '', font_path)
    pdf.set_font('DejaVu', '', 12)
    
    # Очищаем текст от технической метки
    clean_text = text.replace("[PAYWALL]", "").strip()
    
    # Используем write вместо multi_cell. 
    # 10 — это высота строки. write() сам переносит текст и слова.
    pdf.write(10, clean_text)
    
    return pdf.output()

# --- ФУНКЦИЯ СОЗДАНИЯ WORD ---
def create_docx(text):
    doc = Document()
    doc.add_heading('Результат анализа договора - JurisClear AI', 0)
    
    clean_text = text.replace("[PAYWALL]", "").strip()
    
    # Разбиваем текст на параграфы для красоты
    for paragraph in clean_text.split('\n'):
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
        "СТРУКТУРА И ЯЗЫК ОТВЕТА ДОЛЖНЫ СТРОГО СООТВЕТСТВОВАТЬ ЭТАЛОНУ (с [PAYWALL] и SCORE).\n\n"
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
    st.markdown(f"<h1 style='color: white;'>⚖️ JurisClear baylus <span style='color:#3b82f6'>AI</span></h1>", unsafe_allow_html=True)

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
tab_audit, tab_redline, tab_demo, tab_history = st.tabs(["🚀 ИИ Аудит", "🔄 Сравнение версий", "📝 Пример отчета", "📜 История"])

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
                        special_instructions = "Фокус на порядке отчетности агента, расчете вознаграждеия и праве на прямой поиск клиентов."

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

                    # Используем функцию для анализа длинного текста
                    raw_res = analyze_long_text(text, contract_type, user_role, special_instructions, prompt_instruction)
                    
                    # Извлекаем оценку и очищаем текст для интерфейса
                    score_match = re.search(r"SCORE:\s*(\d+)", raw_res)
                    score = int(score_match.group(1)) if score_match else 5
                    clean_res = re.sub(r"SCORE:\s*\d+", "", raw_res).strip()

                    if clean_res:
                        # --- ИНТЕГРИРОВАННЫЙ БЛОК СОХРАНЕНИЯ (ОБНОВЛЕННЫЙ) ---
                        if st.session_state.user:
                            # Берем ID именно из объекта пользователя Supabase
                            current_user_id = st.session_state.user.id 
                            
                            # ПЕЧАТАЕМ ДЛЯ ПРОВЕРКИ (увидишь в терминале/логах)
                            print(f"DEBUG: Попытка сохранения для пользователя: {current_user_id}")

                            data_to_save = {
                                "user_id": current_user_id, # Убедись, что колонка в БД называется именно user_id
                                "contract_type": contract_type,
                                "user_role": user_role,
                                "raw_analysis": raw_res,
                                "payment_status": "pending"
                            }
                            
                            try:
                                # Добавляем .execute() в конце
                                response = supabase.table("contract_audits").insert(data_to_save).execute()
                                st.success("Анализ успешно сохранен в базу!")
                                
                                # Записываем данные в сессию для отображения и делаем реран
                                st.session_state.analysis_result = clean_res
                                st.session_state.current_audit_id = response.data[0]['id']
                                st.session_state.audit_score = score
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Ошибка при сохранении: {e}")
                                # Выведем подробности ошибки для нас
                                print(f"DEBUG ERROR: {e}") 
                        else:
                            st.error("Ошибка: Пользователь не авторизован. Войдите в систему.")
                        # -------------------------------------------------------
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
                        st.markdown(f"<div class='report-card'>{paid_part.strip()}</div>", unsafe_allow_html=True)
                        
                        # Три колонки для кнопок
                        col_pdf, col_word, col_sup = st.columns(3)
                        
                        with col_pdf:
                            pdf_bytes = create_pdf(clean_res)
                            st.download_button(
                                label="📥 PDF",
                                data=bytes(pdf_bytes),
                                file_name=f"audit_{str(current_audit_id)[:8]}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        with col_word:
                            try:
                                word_bytes = create_docx(clean_res)
                                st.download_button(
                                    label="📝 Word",
                                    data=word_bytes,
                                    file_name=f"audit_{str(current_audit_id)[:8]}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error("Ошибка Word")
                        
                        with col_sup:
                            st.link_button("🆘 Поддержка", "https://t.me/твой_логин", use_container_width=True)

                        st.write("")
                        if st.button("📁 Загрузить новый договор", use_container_width=True, key="btn_paid_reset"):
                            st.session_state.reset_counter += 1
                            keys_to_clear = ["analysis_result", "current_audit_id", "audit_score"]
                            for k in keys_to_clear:
                                if k in st.session_state: del st.session_state[k]
                            st.rerun()
                    else:
                        st.warning("🔒 **Полный отчет и Протокол разногласий заблокированы.**")
                        
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

                        if st.button("❌ Отменить и загрузить другой файл", use_container_width=True):
                            st.session_state.reset_counter += 1
                            keys_to_clear = ["analysis_result", "current_audit_id", "audit_score"]
                            for k in keys_to_clear:
                                if k in st.session_state: del st.session_state[k]
                            st.rerun()
                else:
                    st.markdown(f"<div class='report-card'>{clean_res}</div>", unsafe_allow_html=True)
                    
                    col_pdf_f, col_docx_f = st.columns(2)
                    with col_pdf_f:
                        try:
                            pdf_bytes = create_pdf(clean_res)
                            st.download_button(
                                label="📥 Скачать PDF",
                                data=bytes(pdf_bytes),
                                file_name=f"audit_{str(current_audit_id)[:8]}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Ошибка PDF: {e}")
                    
                    with col_docx_f:
                        try:
                            docx_bytes = create_docx(clean_res)
                            st.download_button(
                                label="📥 Скачать Word",
                                data=docx_bytes,
                                file_name=f"audit_{str(current_audit_id)[:8]}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Ошибка Word: {e}")

                    if st.button("📁 Загрузить новый договор", key="btn_no_paywall_reset", use_container_width=True):
                        st.session_state.reset_counter += 1
                        keys_to_clear = ["analysis_result", "current_audit_id", "audit_score"]
                        for k in keys_to_clear:
                            if k in st.session_state: del st.session_state[k]
                        st.rerun()

    else:
        if "analysis_result" in st.session_state:
            keys_to_clear = ["analysis_result", "current_audit_id", "audit_score"]
            for k in keys_to_clear:
                if k in st.session_state: del st.session_state[k]
        st.info("Пожалуйста, загрузите файл договора в формате PDF для начала анализа.")

with tab_redline:
    st.subheader("🔄 Сравнение двух редакций договора")
    st.info("Загрузите исходную версию и версию с правками, чтобы ИИ нашел отличия и оценил риски.")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        file_v1 = st.file_uploader("Исходная версия (PDF)", type=['pdf'], key="v1")
    with col_v2:
        file_v2 = st.file_uploader("Новая версия (PDF)", type=['pdf'], key="v2")
    
    if file_v1 and file_v2:
        if st.button("🚀 Найти отличия", use_container_width=True):
            with st.spinner("ИИ сравнивает документы..."):
                text_v1 = extract_text_from_pdf(file_v1.getvalue())
                text_v2 = extract_text_from_pdf(file_v2.getvalue())
                
                compare_prompt = f"""
                Ты — эксперт-юрист. Твоя задача сравнить две версии одного договора и найти отличия.
                
                ВЕРСИЯ 1 (Исходная):
                {text_v1[:15000]} 
                
                ВЕРСИЯ 2 (С правками):
                {text_v2[:15000]}
                
                АКЦЕНТИРУЙ ВНИМАНИЕ НА:
                1. Изменении сумм, сроков и ответственности.
                2. Удаленных пунктах, которые были важны.
                3. Новых скрытых обязанностях.
                
                ОТВЕТЬ В ВИДЕ ТАБЛИЦЫ:
                | Пункт | Что было (v1) | Что стало (v2) | Риск / Комментарий |
                |-------|---------------|----------------|-------------------|
                """
                
                compare_res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": compare_prompt}],
                    temperature=0.0
                )
                
                st.markdown("### 📊 Результат сравнения")
                st.markdown(compare_res.choices[0].message.content)

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
            history = supabase.table("contract_audits") \
                .select("*") \
                .eq("user_id", st.session_state.user.id) \
                .order("created_at", desc=True) \
                .execute()
            
            if not history.data:
                st.info("У вас пока нет сохраненных анализов.")
            else:
                for audit in history.data:
                    date_str = audit['created_at'][:10] 
                    status = "✅ Оплачено" if audit['payment_status'] == 'paid' else "⏳ Ожидает оплаты"
                    
                    with st.expander(f"📄 {audit['contract_type']} от {date_str} — {status}"):
                        res_text = audit['raw_analysis']
                        if "[PAYWALL]" in res_text and audit['payment_status'] != 'paid':
                            st.markdown(res_text.split("[PAYWALL]")[0])
                            st.warning("Этот отчет не оплачен. Оплатите его в основной вкладке, чтобы открыть полный доступ.")
                        else:
                            st.markdown(res_text.replace("[PAYWALL]", ""))
                            
                            if audit['payment_status'] == 'paid':
                                h_col1, h_col2 = st.columns(2)
                                with h_col1:
                                    try:
                                        pdf_bytes = create_pdf(res_text)
                                        st.download_button(
                                            label="📥 Скачать PDF",
                                            data=bytes(pdf_bytes),
                                            file_name=f"audit_{date_str}.pdf",
                                            mime="application/pdf",
                                            key=f"dl_pdf_{audit['id']}",
                                            use_container_width=True
                                        )
                                    except Exception as e:
                                        st.error(f"Ошибка PDF: {e}")
                                with h_col2:
                                    try:
                                        docx_bytes = create_docx(res_text)
                                        st.download_button(
                                            label="📥 Скачать Word",
                                            data=docx_bytes,
                                            file_name=f"audit_{date_str}.docx",
                                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                            key=f"dl_docx_{audit['id']}",
                                            use_container_width=True
                                        )
                                    except Exception as e:
                                        st.error(f"Ошибка Word: {e}")
                            
        except Exception as e:
            st.error(f"Не удалось загрузить историю: {e}")

st.divider()
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption("© 2026 JurisClear AI")
with col_f2:
    if st.button("Политика конфиденциальности", type="tertiary"):
        st.info("""
        ### Privacy Policy / Политика конфиденциальности
        **Effective Date: February 24, 2026**

        1. **Data Collection:** We collect your email address for account access and the documents you upload for analysis.
        2. **Data Processing:** Your documents are processed via OpenAI API. We do not use your data to train AI models.
        3. **Data Storage:** Your analysis history is stored securely in Supabase. You can delete your data at any time.
        4. **Third Parties:** We use Lemon Squeezy for payments. We do not store your credit card details.

        ---
        1. **Сбор данных:** Мы собираем ваш email для доступа и документы, которые вы загружаете для анализа.
        2. **Обработка:** Документы анализируются через API OpenAI. Ваши данные НЕ используются для обучения моделей.
        3. **Хранение:** История анализов хранится в зашифрованном виде в Supabase.
        4. **Оплата:** Платежи обрабатываются через Lemon Squeezy. Мы не имеем доступа к данным ваших карт.
        """)
with col_f3:
    if st.button("Условия использования", type="tertiary"):
        st.info("""
        ### Terms of Service / Условия использования
        **Last Updated: February 24, 2026**

        1. **Not Legal Advice:** JurisClear AI provides automated document analysis. This is NOT a substitute for professional legal advice. Always consult a qualified lawyer.
        2. **Accuracy:** AI may occasionally produce inaccurate results. JurisClear AI is not liable for any business decisions based on AI reports.
        3. **Refunds:** Due to the nature of digital goods and the costs of AI processing, refunds are not provided once an analysis is generated.
        4. **Subscription/Payments:** Access to full reports is granted upon successful payment via Lemon Squeezy.

        ---
        1. **Не является юридической консультацией:** JurisClear AI предоставляет автоматизированный анализ. Это НЕ замена профессиональному юристу.
        2. **Точность:** ИИ может допускать ошибки. Мы не несем ответственности за ваши бизнес-решения, принятые на основе отчетов.
        3. **Возвраты:** В связи с затратами на ИИ-процессинг, возврат средств после генерации полного отчета невозможен.
        4. **Оплата:** Доступ к полным отчетам предоставляется после подтверждения оплаты через Lemon Squeezy.
        """)
st.caption("© 2026 JurisClear AI | Ереван, Армения | support@jurisclear.com")
