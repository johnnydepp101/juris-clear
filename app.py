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
import uuid
from datetime import datetime
import json
import logging

# --- 0. ЛОГИРОВАНИЕ ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_action(message, data=None):
    """Подробное логирование для отладки"""
    if data:
        logger.info(f"{message} | DATA: {json.dumps(data, default=str, ensure_ascii=False)}")
        # Также выводим в Streamlit для пользователя, если включен режим отладки
        if st.session_state.get("debug_mode"):
            st.write(f"🔍 DEBUG: {message}")
            st.json(data)
    else:
        logger.info(message)
        if st.session_state.get("debug_mode"):
            st.write(f"🔍 DEBUG: {message}")

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

if 'profile' not in st.session_state:
    st.session_state.profile = None

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# (Авторизация удалена по требованию пользователя)

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
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets.get("SUPABASE_SERVICE_KEY") or st.secrets.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Ошибка подключения к Supabase: {e}. Проверьте secrets.toml")
    supabase = None

# --- ФУНКЦИИ АУТЕНТИФИКАЦИИ ---
def sign_in(email, password):
    if not supabase: return False
    try:
        log_action("Попытка входа", {"email": email})
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            st.session_state.user = response.user
            get_profile(response.user.id)
            log_action("Вход успешен", {"user_id": response.user.id})
            return True
    except Exception as e:
        st.error(f"Ошибка входа: {e}")
        log_action("Ошибка входа", {"error": str(e)})
    return False

def sign_up(email, password):
    if not supabase: return False
    try:
        log_action("Попытка регистрации", {"email": email})
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success("Регистрация успешна! Теперь вы можете войти.")
            log_action("Регистрация успешна", {"user_id": response.user.id})
            return True
    except Exception as e:
        st.error(f"Ошибка регистрации: {e}")
        log_action("Ошибка регистрации", {"error": str(e)})
    return False

def sign_out():
    if not supabase: return
    log_action("Выход из системы", {"user_id": st.session_state.user.id if st.session_state.user else "N/A"})
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.profile = None
    st.rerun()

def get_profile(user_id):
    if not supabase: return None
    try:
        log_action("Получение профиля", {"user_id": user_id})
        res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        if res.data:
            st.session_state.profile = res.data
            log_action("Профиль получен", res.data)
            return res.data
    except Exception as e:
        log_action("Ошибка получения профиля", {"error": str(e)})
    return None

def save_audit(file_name, contract_type, user_role, analysis_text, score, is_paid=False):
    if not supabase: return None
    try:
        user_id = st.session_state.user.id if st.session_state.user else None
        data = {
            "user_id": user_id,
            "file_name": file_name,
            "contract_type": contract_type,
            "user_role": user_role,
            "analysis_text": analysis_text,
            "score": score,
            "is_paid_one_off": is_paid,
            "session_id": st.session_state.session_id if not user_id else None
        }
        log_action("Сохранение аудита", {k: v for k, v in data.items() if k != "analysis_text"})
        res = supabase.table("audits").insert(data).execute()
        if res.data:
            new_id = res.data[0]['id']
            log_action("Аудит сохранен", {"id": new_id})
            return new_id
    except Exception as e:
        log_action("Ошибка сохранения аудита", {"error": str(e)})
    return None

def get_user_audits():
    if not supabase or not st.session_state.user: return []
    try:
        log_action("Запрос истории аудитов", {"user_id": st.session_state.user.id})
        res = supabase.table("audits").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        log_action("Ошибка получения истории", {"error": str(e)})
        return []

def get_user_status():
    if not st.session_state.user:
        return "guest"
    if st.session_state.profile and st.session_state.profile.get("subscription_status") == "pro":
        return "pro"
    return "free"

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
    if not text:
        return None
        
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
    if not text:
        return None
        
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
        # Отображаем email и кнопку выхода, если пользователь вошел
        user_email = st.session_state.user.email
        status = get_user_status()
        status_color = "var(--accent-green)" if status == "pro" else "var(--secondary-text)"
        
        st.markdown(f"""
            <div style="text-align: right;">
                <div style="font-size: 14px; font-weight: 600;">{user_email}</div>
                <div style="font-size: 12px; color: {status_color}; text-transform: uppercase;">Статус: {status}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Выйти", key="logout_btn", use_container_width=True):
            sign_out()
    else:
        # Кнопки входа/регистрации, если не вошел
        with st.popover("🔑 Войти / Регистрация", use_container_width=True):
            auth_mode = st.radio("Действие", ["Вход", "Регистрация"], horizontal=True, label_visibility="collapsed")
            email = st.text_input("Email", key="auth_email")
            password = st.text_input("Пароль", type="password", key="auth_password")
            
            if auth_mode == "Вход":
                if st.button("Войти", type="primary", use_container_width=True):
                    if sign_in(email, password):
                        st.rerun()
            else:
                if st.button("Зарегистрироваться", type="primary", use_container_width=True):
                    if sign_up(email, password):
                        st.info("Проверьте email для подтверждения (если включено) или попробуйте войти.")

st.markdown(f"<p style='text-align: center; color: var(--secondary-text); font-weight: 500;'>Профессиональный юридический аудит договоров</p>", unsafe_allow_html=True)

# Кнопка отладки (для пользователя по запросу)
with st.expander("🛠️ Отладка"):
    st.session_state.debug_mode = st.toggle("Включить подробные логи", value=st.session_state.debug_mode)
    if st.button("Очистить кэш сессии"):
        st.session_state.clear()
        st.rerun()

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
    # URL для оплаты подписки с привязкой к user_id
    user_id = st.session_state.user.id if st.session_state.user else "new_user"
    sub_checkout_url = f"https://jurisclearai.lemonsqueezy.com/checkout/buy/69a180c9-d5f5-4018-9dbe-b8ac64e4ced8?checkout[custom][user_id]={user_id}"
    
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
                <a href="{sub_checkout_url}" target="_blank" style="display: block; background: white; color: #1d4ed8; text-align: center; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 15px;">🚀 Оформить подписку</a>
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

# Определение доступных вкладок
user_status = get_user_status()
tabs_list = ["🚀 ИИ Аудит", "📝 Пример отчета"]

if user_status != "guest":
    tabs_list.insert(1, "🔄 Сравнение версий")
    if user_status == "pro":
        tabs_list.append("📁 История")

tabs = st.tabs(tabs_list)

# Распределение логики по индексам (нужно учитывать динамический список)
tab_audit = tabs[0]
idx = 1
tab_redline = None
if user_status != "guest":
    tab_redline = tabs[idx]
    idx += 1
tab_demo = tabs[idx]
idx += 1
tab_history = tabs[idx] if user_status == "pro" else None

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
                        
                        # СОХРАНЕНИЕ В БД
                        audit_db_id = None
                        if st.session_state.user:
                            # Для обычных и про сохраняем в БД
                            audit_db_id = save_audit(file.name, contract_type, user_role, clean_res, score)
                            st.session_state.current_audit_db_id = audit_db_id
                            log_action("Результат сохранен для зарегистрированного пользователя", {"audit_id": audit_db_id})
                        else:
                            # Для гостей создаем временную запись для оплаты
                            audit_db_id = save_audit(file.name, contract_type, user_role, clean_res, score)
                            st.session_state.current_audit_db_id = audit_db_id
                            st.session_state.temp_audit_id = audit_db_id # Используем ID из БД вместо UUID для гостей тоже
                            log_action("Создана запись в БД для гостя", {"audit_id": audit_db_id})
                            
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
                user_status = get_user_status()
                
                # --- ЛОГИКА ОГРАНИЧЕНИЯ ДОСТУПА ---
                is_unlocked = (user_status == "pro") or st.session_state.get("is_paid_one_off", False)
                
                if not is_unlocked:
                    # Показываем только часть (Резюме и Риски), остальное блюрим
                    parts = clean_res.split("## 🛠️ Протокол разногласий")
                    preview_text = parts[0]
                    
                    st.markdown(f"<div class='report-card'>{preview_text.strip()}</div>", unsafe_allow_html=True)
                    
                    st.markdown("""
                        <div style="background: rgba(59, 130, 246, 0.1); border: 2px dashed #3b82f6; padding: 30px; border-radius: 15px; text-align: center; margin-top: 20px;">
                            <h3 style="color: #3b82f6; margin-top: 0;">🔒 Полный отчет заблокирован</h3>
                            <p>Чтобы увидеть <b>Протокол разногласий</b> с готовыми правками и скачать отчет в <b>PDF/Word</b>, приобретите разовый аудит или оформите подписку.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Кнопка разовой оплаты
                    audit_payment_id = st.session_state.get("current_audit_db_id", "unknown")
                    one_off_url = f"https://jurisclearai.lemonsqueezy.com/checkout/buy/a06e3832-bc7a-4d2c-8f1e-113446b2bf61?checkout[custom][audit_id]={audit_payment_id}"
                    
                    col_pay1, col_pay2 = st.columns(2)
                    with col_pay1:
                        st.link_button("💳 Купить разовый аудит (850 ₽)", one_off_url, use_container_width=True, type="primary")
                    with col_pay2:
                        st.info("💡 Подписка Pro выгоднее, если у вас много документов!")
                else:
                    # ПОЛНЫЙ ДОСТУП
                    st.markdown(f"<div class='report-card'>{clean_res.strip()}</div>", unsafe_allow_html=True)
                
                # Три колонки для кнопок (ID заменен на фейковый или удален)
                col_pdf, col_word, col_sup = st.columns(3)
                
                with col_pdf:
                    if is_unlocked:
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
                        st.button("📥 PDF (Заблокировано)", disabled=True, use_container_width=True)
                
                with col_word:
                    if is_unlocked:
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
                        except Exception as e:
                            st.error("Ошибка Word")
                    else:
                        st.button("📝 Word (Заблокировано)", disabled=True, use_container_width=True)
                
                with col_sup:
                    st.link_button("🆘 Поддержка", "mailto:support@jurisclear.com", use_container_width=True)

                st.write("")
                if st.button("📁 Загрузить новый договор", use_container_width=True, key="btn_paid_reset"):
                    st.session_state.reset_counter += 1
                    keys_to_clear = ["analysis_result", "audit_score", "temp_audit_id", "is_paid_one_off"]
                    for k in keys_to_clear:
                        if k in st.session_state: del st.session_state[k]
                    st.rerun()
if tab_redline is not None:
    with tab_redline:
        if user_status == "guest":
            st.warning("🔄 Сравнение версий доступно только для зарегистрированных пользователей.")
            st.info("Пожалуйста, войдите или зарегистрируйтесь, чтобы использовать эту функцию.")
        else:
            st.markdown("### 🔄 Сравнение версий договора")
            st.write("Загрузите две версии одного документа, чтобы увидеть различия.")
            
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                file1 = st.file_uploader("Версия №1 (Оригинал)", type=['pdf'], key="redline_v1")
            with col_v2:
                file2 = st.file_uploader("Версия №2 (С правками)", type=['pdf'], key="redline_v2")
                
            if file1 and file2:
                if st.button("Сравнить версии", type="primary", use_container_width=True):
                    with st.spinner("ИИ анализирует различия..."):
                        try:
                            text1_raw = extract_text_from_pdf(file1.read())
                            text2_raw = extract_text_from_pdf(file2.read())
                            
                            text1_str = str(text1_raw)
                            text2_str = str(text2_raw)
                            
                            prompt = f"""
                            Ты — юрист. Сравни эти два текста договора. 
                            Выдели ЧТО ИМЕННО изменилось и КАКИЕ РИСКИ это несет.
                            Текст 1: {text1_str[:5000]}...
                            Текст 2: {text2_str[:5000]}...
                            
                            Ответ дай в формате: Список изменений, Анализ рисков новых правок.
                            """
                            response = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": prompt}]
                            )
                            diff_res = response.choices[0].message.content
                            st.markdown(f"<div class='report-card'>{diff_res}</div>", unsafe_allow_html=True)
                            
                            # Кнопки скачивания
                            c_p, c_w = st.columns(2)
                            with c_p:
                                p_b = create_pdf(diff_res)
                                if p_b: st.download_button("📥 PDF", p_b, "diff.pdf", "application/pdf", use_container_width=True)
                            with c_w:
                                w_b = create_docx(diff_res)
                                if w_b: st.download_button("📝 Word", w_b, "diff.docx", use_container_width=True)
                        except Exception as e:
                            st.error(f"Ошибка сравнения: {e}")

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

if tab_history is not None:
    with tab_history:
        st.markdown("### 📁 Ваша история анализов")
        audits = get_user_audits()
        if not audits:
            st.info("У вас пока нет сохраненных анализов.")
        else:
            for audit in audits:
                audit_date = datetime.fromisoformat(audit['created_at']).strftime('%d.%m.%Y %H:%M')
                with st.expander(f"📄 {audit['file_name']} (от {audit_date})"):
                    st.write(f"**Тип:** {audit['contract_type']} | **Роль:** {audit['user_role']}")
                    
                    bar_c, bar_s, risk_t = get_risk_params(audit['score'])
                    st.markdown(f"""
                        <div style="height:20px; width:{audit['score']*10}%; background:{bar_c}; border-radius:5px; margin-bottom:10px;"></div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"<div style='background: var(--card-bg); padding:15px; border-radius:10px;'>{audit['analysis_text'][:1000]}...</div>", unsafe_allow_html=True)
                    
                    c_p, c_w = st.columns(2)
                    audit_uuid_str = str(audit['id'])
                    with c_p:
                        p_b = create_pdf(audit['analysis_text'])
                        if p_b: st.download_button("📥 PDF", p_b, f"audit_{audit_uuid_str[:8]}.pdf", use_container_width=True, key=f"p_{audit_uuid_str}")
                    with c_w:
                        w_b = create_docx(audit['analysis_text'])
                        if w_b: st.download_button("📝 Word", w_b, f"audit_{audit_uuid_str[:8]}.docx", use_container_width=True, key=f"w_{audit_uuid_str}")

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
