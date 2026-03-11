import streamlit as st
from openai import OpenAI
import pdfplumber
import re
from supabase import create_client, Client
import os
from fpdf import FPDF
from docx import Document
from io import BytesIO
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import uuid
from datetime import datetime, timezone
import streamlit.components.v1 as components
import json

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
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'auth_user' not in st.session_state:
    st.session_state.auth_user = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'current_audit_paid' not in st.session_state:
    st.session_state.current_audit_paid = False
if 'current_audit_id' not in st.session_state:
    st.session_state.current_audit_id = None
if 'auth_restored' not in st.session_state:
    st.session_state.auth_restored = False

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
except Exception as e:
    st.error(f"Ошибка подключения к Supabase: {e}. Проверьте secrets.toml")
    # Создаем фиктивный клиент, чтобы приложение не вылетало сразу при отрисовке UI
    supabase = None

# --- LEMON SQUEEZY URLs ---
LS_SINGLE_AUDIT_URL = "https://jurisclearai.lemonsqueezy.com/checkout/buy/0fb5f2af-1335-4dfd-9091-ea9aa9eb6303"
LS_PRO_SUB_URL = "https://jurisclearai.lemonsqueezy.com/checkout/buy/8bc12198-0e4d-4774-b486-78ddcb5a200c"

# --- ФУНКЦИИ АВТОРИЗАЦИИ ---
def get_user_role():
    """Определяет роль: guest / registered / subscriber"""
    if not st.session_state.auth_user:
        return "guest"
    profile = st.session_state.user_profile
    if profile and profile.get("subscription_status") == "active":
        # Проверяем что подписка не истекла
        expires = profile.get("subscription_expires_at")
        if expires:
            try:
                exp_dt = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                if exp_dt > datetime.now(timezone.utc):
                    return "subscriber"
            except:
                pass
    return "registered"

def load_user_profile():
    """Загружает профиль текущего пользователя из БД"""
    if supabase and st.session_state.auth_user:
        try:
            uid = st.session_state.auth_user.id
            res = supabase.table("profiles").select("*").eq("id", uid).maybe_single().execute()
            if res.data:
                st.session_state.user_profile = res.data
        except Exception as e:
            pass  # Не ломаем UI если не можем загрузить профиль

def do_login(email, password):
    """Логин через Supabase Auth"""
    if not supabase:
        return False, "Нет подключения к базе данных"
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.auth_user = res.user
        # Сброс session_id при логине чтобы гостевые оплаты не текли
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.current_audit_paid = False
        st.session_state.current_audit_id = None
        load_user_profile()
        # Сохраняем токены для persistence
        if res.session:
            save_auth_to_localstorage(res.session.access_token, res.session.refresh_token)
        return True, "Успешный вход!"
    except Exception as e:
        msg = str(e)
        if "Invalid login" in msg or "invalid" in msg.lower():
            return False, "Неверный email или пароль"
        return False, f"Ошибка входа: {msg}"

def do_signup(email, password):
    """Регистрация через Supabase Auth"""
    if not supabase:
        return False, "Нет подключения к базе данных"
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            st.session_state.auth_user = res.user
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.current_audit_paid = False
            st.session_state.current_audit_id = None
            load_user_profile()
            if res.session:
                save_auth_to_localstorage(res.session.access_token, res.session.refresh_token)
            return True, "Регистрация успешна!"
        return False, "Не удалось зарегистрироваться"
    except Exception as e:
        msg = str(e)
        if "already registered" in msg.lower() or "already been registered" in msg.lower():
            return False, "Этот email уже зарегистрирован"
        if "password" in msg.lower():
            return False, "Пароль должен быть не менее 6 символов"
        return False, f"Ошибка регистрации: {msg}"

def do_logout():
    """Выход из аккаунта"""
    if supabase:
        try:
            supabase.auth.sign_out()
        except:
            pass
    st.session_state.auth_user = None
    st.session_state.user_profile = None
    st.session_state.current_audit_paid = False
    st.session_state.current_audit_id = None
    st.session_state.session_id = str(uuid.uuid4())
    # Очищаем localStorage
    clear_auth_from_localstorage()
    clear_analysis_from_localstorage()

def split_analysis(full_text):
    """Разделяет анализ на бесплатную и платную части по маркеру протокола"""
    markers = ["## 🛠️ Протокол разногласий", "## 🛠️ Протокол", "## Протокол разногласий", "🛠️ Протокол разногласий"]
    for marker in markers:
        idx = full_text.find(marker)
        if idx != -1:
            return full_text[:idx].strip(), full_text[idx:].strip()
    # Если маркер не найден — 70% бесплатно, 30% платно
    split_point = int(len(full_text) * 0.7)
    # Ищем ближайший перенос строки для чистого разделения
    newline_pos = full_text.find('\n', split_point)
    if newline_pos != -1:
        split_point = newline_pos
    return full_text[:split_point].strip(), full_text[split_point:].strip()

def build_checkout_url(base_url, user_id=None, session_id=None, email=None):
    """Строит URL для Lemon Squeezy Overlay с custom_data"""
    params = []
    if session_id:
        params.append(f"checkout[custom][session_id]={session_id}")
    if user_id:
        params.append(f"checkout[custom][user_id]={user_id}")
    if email:
        params.append(f"checkout[email]={email}")
    params.append("embed=1")  # Для overlay mode
    if params:
        return base_url + "?" + "&".join(params)
    return base_url

# --- СОХРАНЕНИЕ АУДИТА В БД ---
def save_audit_to_db(file_name, contract_type, user_role_str, risk_score, full_analysis):
    """Сохраняет результат анализа в таблицу audits"""
    if not supabase:
        return None
    try:
        free_part, paid_part = split_analysis(full_analysis)
        user_id = None
        if st.session_state.auth_user:
            user_id = st.session_state.auth_user.id
        
        insert_data = {
            "session_id": st.session_state.session_id,
            "file_name": file_name or "document.pdf",
            "contract_type": contract_type or "Авто-определение",
            "user_role": user_role_str or "Заказчик",
            "risk_score": risk_score,
            "analysis_free": free_part,
            "analysis_paid": paid_part,
            "is_paid": False,
        }
        if user_id:
            insert_data["user_id"] = user_id
        
        res = supabase.table("audits").insert(insert_data).execute()
        if res.data:
            return res.data[0].get("id")
    except Exception as e:
        pass  # Не ломаем UX если запись не удалась
    return None

# --- LOCALSTORAGE PERSISTENCE ---
def save_auth_to_localstorage(access_token, refresh_token):
    """Сохраняет токены авторизации в localStorage браузера"""
    components.html(f"""
        <script>
            localStorage.setItem('jc_access_token', '{access_token}');
            localStorage.setItem('jc_refresh_token', '{refresh_token}');
        </script>
    """, height=0)

def clear_auth_from_localstorage():
    """Очищает токены из localStorage"""
    components.html("""
        <script>
            localStorage.removeItem('jc_access_token');
            localStorage.removeItem('jc_refresh_token');
        </script>
    """, height=0)

def save_analysis_to_localstorage(analysis, score, file_name, audit_id):
    """Сохраняет результат анализа в localStorage"""
    safe_analysis = json.dumps(analysis, ensure_ascii=False)
    components.html(f"""
        <script>
            localStorage.setItem('jc_analysis', {safe_analysis});
            localStorage.setItem('jc_score', '{score}');
            localStorage.setItem('jc_file_name', '{file_name}');
            localStorage.setItem('jc_audit_id', '{audit_id or ""}');
        </script>
    """, height=0)

def clear_analysis_from_localstorage():
    """Очищает анализ из localStorage"""
    components.html("""
        <script>
            localStorage.removeItem('jc_analysis');
            localStorage.removeItem('jc_score');
            localStorage.removeItem('jc_file_name');
            localStorage.removeItem('jc_audit_id');
        </script>
    """, height=0)

def render_ls_checkout(checkout_url, button_text):
    """Рендерит кнопку Lemon Squeezy с overlay checkout внутри страницы"""
    components.html(f"""
        <script src="https://app.lemonsqueezy.com/js/lemon.js" defer></script>
        <style>
            .ls-checkout-btn {{
                display: block;
                width: 100%;
                padding: 14px 24px;
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                text-decoration: none;
                text-align: center;
                box-sizing: border-box;
                transition: all 0.2s;
                font-family: inherit;
            }}
            .ls-checkout-btn:hover {{
                box-shadow: 0 6px 20px rgba(59,130,246,0.5);
                transform: translateY(-1px);
            }}
        </style>
        <a href="{checkout_url}" class="lemonsqueezy-button ls-checkout-btn">
            {button_text}
        </a>
        <script>
            // Делаем iframe полноэкранным когда overlay открыт
            (function() {{
                var frame = window.frameElement;
                if (!frame) return;
                var origStyle = {{}};
                
                var observer = new MutationObserver(function(mutations) {{
                    var overlay = document.querySelector('.lemon-overlay, .ll-overlay, iframe[src*="lemonsqueezy"]');
                    if (overlay && frame.style.position !== 'fixed') {{
                        origStyle = {{
                            position: frame.style.position,
                            top: frame.style.top,
                            left: frame.style.left,
                            width: frame.style.width,
                            height: frame.style.height,
                            zIndex: frame.style.zIndex
                        }};
                        frame.style.position = 'fixed';
                        frame.style.top = '0';
                        frame.style.left = '0'; 
                        frame.style.width = '100vw';
                        frame.style.height = '100vh';
                        frame.style.zIndex = '99999';
                    }}
                }});
                observer.observe(document.body, {{ childList: true, subtree: true }});
                
                // Восстанавливаем при закрытии
                window.addEventListener('message', function(e) {{
                    if (e.data === 'lr:close' || (e.data && e.data.event === 'Checkout.Success')) {{
                        frame.style.position = origStyle.position || '';
                        frame.style.top = origStyle.top || '';
                        frame.style.left = origStyle.left || '';
                        frame.style.width = origStyle.width || '';
                        frame.style.height = origStyle.height || '';
                        frame.style.zIndex = origStyle.zIndex || '';
                        
                        if (e.data && e.data.event === 'Checkout.Success') {{
                            // Перезагружаем страницу после успешной оплаты
                            window.parent.location.reload();
                        }}
                    }}
                }});
            }})();
        </script>
    """, height=55, scrolling=False)

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

# --- 5. ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---

# --- ВОССТАНОВЛЕНИЕ АВТОРИЗАЦИИ ИЗ LOCALSTORAGE ---
if not st.session_state.auth_user and not st.session_state.auth_restored:
    # Пробуем восстановить сессию из query params (устанавливаются JS-ом ниже)
    qp = st.query_params
    if 'jc_at' in qp and 'jc_rt' in qp and supabase:
        try:
            at = qp['jc_at']
            rt = qp['jc_rt']
            res = supabase.auth.set_session(at, rt)
            if res and res.user:
                st.session_state.auth_user = res.user
                load_user_profile()
        except:
            pass
        st.session_state.auth_restored = True
        # Очищаем query params
        st.query_params.clear()
        st.rerun()
    else:
        st.session_state.auth_restored = True
        # JS: читаем localStorage и ставим query params если есть токены
        components.html("""
            <script>
                (function() {
                    var at = localStorage.getItem('jc_access_token');
                    var rt = localStorage.getItem('jc_refresh_token');
                    if (at && rt) {
                        var url = new URL(window.parent.location);
                        if (!url.searchParams.has('jc_at')) {
                            url.searchParams.set('jc_at', at);
                            url.searchParams.set('jc_rt', rt);
                            window.parent.location.replace(url.toString());
                        }
                    }
                })();
            </script>
        """, height=0)

# --- АВТО-ПРОВЕРКА ОПЛАТЫ ПРИ ЗАГРУЗКЕ ---
if not st.session_state.current_audit_paid and st.session_state.current_audit_id and supabase:
    try:
        audit_res = supabase.table("audits").select("is_paid").eq("id", st.session_state.current_audit_id).maybe_single().execute()
        if audit_res.data and audit_res.data.get("is_paid"):
            st.session_state.current_audit_paid = True
    except:
        pass

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
    role = get_user_role()
    if role == "guest":
        auth_c1, auth_c2 = st.columns(2)
        with auth_c1:
            if st.button("Войти", key="btn_login_header", use_container_width=True, type="tertiary"):
                st.session_state.show_login = True
                st.session_state.show_signup = False
                st.rerun()
        with auth_c2:
            if st.button("Регистрация", key="btn_signup_header", use_container_width=True, type="primary"):
                st.session_state.show_signup = True
                st.session_state.show_login = False
                st.rerun()
    else:
        user_email = st.session_state.auth_user.email if st.session_state.auth_user else ""
        role_badge = "🟢 Pro" if role == "subscriber" else "👤"
        st.markdown(f"<p style='text-align:right; font-size:13px; color:var(--secondary-text); margin:0;'>{role_badge} {user_email}</p>", unsafe_allow_html=True)
        if st.button("Выйти", key="btn_logout_header", type="tertiary", use_container_width=True):
            do_logout()
            st.rerun()

# --- ДИАЛОГИ ВХОДА / РЕГИСТРАЦИИ ---
@st.dialog("Вход в аккаунт")
def login_dialog():
    email = st.text_input("Email", key="login_email_input")
    password = st.text_input("Пароль", type="password", key="login_password_input")
    if st.button("Войти", use_container_width=True, type="primary", key="btn_do_login"):
        if email and password:
            ok, msg = do_login(email, password)
            if ok:
                st.success(msg)
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error(msg)
        else:
            st.warning("Заполните все поля")
    st.markdown("---")
    st.caption("Нет аккаунта?")
    if st.button("Зарегистрироваться", use_container_width=True, key="btn_switch_to_signup"):
        st.session_state.show_login = False
        st.session_state.show_signup = True
        st.rerun()

@st.dialog("Регистрация")
def signup_dialog():
    email = st.text_input("Email", key="signup_email_input")
    password = st.text_input("Пароль (мин. 6 символов)", type="password", key="signup_password_input")
    password2 = st.text_input("Повторите пароль", type="password", key="signup_password2_input")
    if st.button("Зарегистрироваться", use_container_width=True, type="primary", key="btn_do_signup"):
        if not email or not password:
            st.warning("Заполните все поля")
        elif password != password2:
            st.error("Пароли не совпадают")
        elif len(password) < 6:
            st.error("Пароль должен быть не менее 6 символов")
        else:
            ok, msg = do_signup(email, password)
            if ok:
                st.success(msg)
                st.session_state.show_signup = False
                st.rerun()
            else:
                st.error(msg)
    st.markdown("---")
    st.caption("Уже есть аккаунт?")
    if st.button("Войти", use_container_width=True, key="btn_switch_to_login"):
        st.session_state.show_signup = False
        st.session_state.show_login = True
        st.rerun()

# Открываем диалоги
if st.session_state.show_login:
    login_dialog()
if st.session_state.show_signup:
    signup_dialog()

st.markdown(f"<p style='text-align: center; color: var(--secondary-text); font-weight: 500;'>Профессиональный юридический аудит договоров</p>", unsafe_allow_html=True)

# --- ОПРЕДЕЛЯЕМ РОЛЬ ДЛЯ UI ---
role = get_user_role()

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
    # --- КНОПКА ПОДПИСКИ ЗАВИСИТ ОТ РОЛИ ---
    if role == "guest":
        sub_button_html = '<div style="display: block; background: rgba(255,255,255,0.15); color: rgba(255,255,255,0.6); text-align: center; padding: 12px; border-radius: 10px; font-weight: 600; font-size: 13px;">🔒 Зарегистрируйтесь для подписки</div>'
    elif role == "subscriber":
        profile = st.session_state.user_profile or {}
        expires = profile.get("subscription_expires_at", "")
        try:
            exp_dt = datetime.fromisoformat(expires.replace('Z', '+00:00'))
            exp_str = exp_dt.strftime("%d.%m.%Y")
        except:
            exp_str = "—"
        sub_button_html = f'<div style="display: block; background: rgba(16,185,129,0.3); color: white; text-align: center; padding: 12px; border-radius: 10px; font-weight: 700; font-size: 14px;">✅ Подписка активна до {exp_str}</div>'
    else:
        # registered — может оформить подписку
        user_id = st.session_state.auth_user.id if st.session_state.auth_user else ""
        user_email = st.session_state.auth_user.email if st.session_state.auth_user else ""
        checkout_sub_url = build_checkout_url(LS_PRO_SUB_URL, user_id=user_id, email=user_email)
        sub_button_html = f'<a href="{checkout_sub_url}" target="_blank" style="display: block; background: white; color: #1d4ed8; text-align: center; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 15px;">🚀 Оформить подписку</a>'

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
                {sub_button_html}
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

# --- РАБОЧЕЕ ПРОСТРАНСТВО (ВКЛАДКИ ПО РОЛЯМ) ---
if role == "subscriber":
    tab_audit, tab_redline, tab_demo, tab_history = st.tabs(["🚀 ИИ Аудит", "🔄 Сравнение версий", "📝 Пример отчета", "📂 История"])
elif role == "registered":
    tab_audit, tab_redline, tab_demo = st.tabs(["🚀 ИИ Аудит", "🔄 Сравнение версий", "📝 Пример отчета"])
    tab_history = None
else:  # guest
    tab_audit, tab_demo = st.tabs(["🚀 ИИ Аудит", "📝 Пример отчета"])
    tab_redline = None
    tab_history = None

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
                        # Сохраняем метаданные для истории
                        st.session_state.audit_file_name = file.name
                        st.session_state.audit_contract_type = contract_type
                        st.session_state.audit_user_role = user_role
                        # Сохраняем аудит в БД
                        audit_id = save_audit_to_db(file.name, contract_type, user_role, score, clean_res)
                        st.session_state.current_audit_id = audit_id
                        st.session_state.current_audit_paid = False
                        # Сохраняем в localStorage
                        save_analysis_to_localstorage(clean_res, score, file.name, audit_id)
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
                clean_res = st.session_state.analysis_result
                
                # --- PAYWALL: разделяем контент ---
                free_part, paid_part = split_analysis(clean_res)
                has_full_access = (role == "subscriber") or st.session_state.get("current_audit_paid", False)
                
                if has_full_access:
                    # Полный доступ — показываем всё
                    st.success("✅ Анализ и протокол разногласий успешно сформированы!")
                    st.markdown(f"<div class='report-card'>{clean_res.strip()}</div>", unsafe_allow_html=True)
                    
                    # Отступ перед кнопками
                    st.write("")
                    
                    # Три колонки для кнопок
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
                        st.link_button("🆘 Поддержка", "https://t.me/JurisClearSupport", use_container_width=True)

                else:
                    # Бесплатная часть + paywall
                    st.success("✅ Предварительный анализ готов!")
                    st.markdown(f"<div class='report-card'>{free_part.strip()}</div>", unsafe_allow_html=True)
                    
                    # Блок paywall с blur-эффектом
                    st.markdown("""
                        <div style="position: relative; margin-top: 20px;">
                            <div style="filter: blur(6px); -webkit-filter: blur(6px); pointer-events: none; 
                                        max-height: 200px; overflow: hidden; opacity: 0.5;">
                                <div class='report-card'>
                                    <h3>🛠️ Протокол разногласий (Готовые правки)</h3>
                                    <table><tr><td>№ Пункта</td><td>Оригинальный текст</td><td>Предлагаемая редакция</td><td>Обоснование</td></tr>
                                    <tr><td>п. 6.1</td><td>Штраф 1% в день...</td><td>Снизить до 0.1%...</td><td>Несоразмерность...</td></tr></table>
                                </div>
                            </div>
                            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                                        display: flex; align-items: center; justify-content: center;">
                                <div style="background: var(--card-bg); backdrop-filter: blur(10px); padding: 30px; 
                                            border-radius: 16px; border: 1px solid var(--accent-blue); text-align: center;
                                            box-shadow: 0 8px 32px rgba(59,130,246,0.3);">
                                    <p style="font-size: 18px; font-weight: 700; margin-bottom: 5px;">🔒 Полный отчёт заблокирован</p>
                                    <p style="font-size: 13px; color: var(--secondary-text); margin-bottom: 15px;">Детальный разбор + Протокол разногласий + Скачивание PDF/Word</p>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")
                    # Кнопка оплаты разового аудита — оверлей Lemon Squeezy
                    user_id_for_checkout = st.session_state.auth_user.id if st.session_state.auth_user else None
                    user_email_for_checkout = st.session_state.auth_user.email if st.session_state.auth_user else None
                    session_id_for_checkout = st.session_state.session_id
                    
                    checkout_url = build_checkout_url(
                        LS_SINGLE_AUDIT_URL,
                        user_id=user_id_for_checkout,
                        session_id=session_id_for_checkout,
                        email=user_email_for_checkout
                    )
                    
                    # Оверлей checkout вместо редиректа
                    render_ls_checkout(checkout_url, "💳 Купить разовый аудит — 850 ₽")
                    
                    # Кнопка проверки оплаты (резервная)
                    if st.button("🔄 Обновить статус оплаты", use_container_width=True, key="btn_check_payment"):
                        if supabase and st.session_state.current_audit_id:
                            try:
                                chk = supabase.table("audits").select("is_paid").eq("id", st.session_state.current_audit_id).maybe_single().execute()
                                if chk.data and chk.data.get("is_paid"):
                                    st.session_state.current_audit_paid = True
                                    st.success("✅ Оплата подтверждена!")
                                    st.rerun()
                                else:
                                    st.info("⏳ Оплата ещё не обработана. Подождите 10-30 секунд.")
                            except Exception as e:
                                st.error(f"Ошибка проверки: {e}")

                st.write("")
                if st.button("📁 Загрузить новый договор", use_container_width=True, key="btn_paid_reset"):
                    st.session_state.reset_counter += 1
                    keys_to_clear = ["analysis_result", "audit_score", "current_audit_paid", "current_audit_id", "audit_file_name", "audit_contract_type", "audit_user_role"]
                    for k in keys_to_clear:
                        if k in st.session_state: del st.session_state[k]
                    clear_analysis_from_localstorage()
                    st.rerun()

# --- ВКЛАДКА СРАВНЕНИЕ ВЕРСИЙ ---
if tab_redline is not None:
    with tab_redline:
        st.write("### 🔄 Сравнение двух версий договора")
        st.markdown("""
            <p style="color: var(--secondary-text); font-size: 0.9em;">
                Загрузите старую и новую версию договора для сравнения. ИИ найдёт все изменения и оценит их значимость.
            </p>
        """, unsafe_allow_html=True)
        
        comp_c1, comp_c2 = st.columns(2)
        with comp_c1:
            file_old = st.file_uploader("📄 Старая версия (PDF)", type=['pdf'], key="comp_old_file")
        with comp_c2:
            file_new = st.file_uploader("📄 Новая версия (PDF)", type=['pdf'], key="comp_new_file")
        
        if file_old and file_new:
            if "comparison_result" not in st.session_state:
                if st.button("🔍 Сравнить документы", use_container_width=True, type="primary", key="btn_compare"):
                    with st.spinner("ИИ сравнивает документы..."):
                        try:
                            old_bytes = file_old.read()
                            new_bytes = file_new.read()
                            old_text = extract_text_from_pdf(old_bytes)
                            new_text = extract_text_from_pdf(new_bytes)
                            
                            if not old_text.strip() or not new_text.strip():
                                st.error("Не удалось извлечь текст из одного или обоих документов.")
                                st.stop()
                            
                            # Ограничиваем размер текста для сравнения
                            max_chars = 15000
                            old_text_trimmed = old_text[:max_chars]
                            new_text_trimmed = new_text[:max_chars]
                            
                            compare_prompt = f"""Ты — опытный юрист. Сравни две версии договора и найди ВСЕ изменения.

СТАРАЯ ВЕРСИЯ:
{old_text_trimmed}

НОВАЯ ВЕРСИЯ:
{new_text_trimmed}

СТРУКТУРА ОТВЕТА (ОБЯЗАТЕЛЬНО на русском):
## 📊 Результат сравнения

### Общее резюме изменений
Кратко опиши что изменилось.

### Таблица изменений
| № | Тип | Было (старая версия) | Стало (новая версия) | Оценка |
| :--- | :--- | :--- | :--- | :--- |

Тип: ➕ Добавлено / ❌ Удалено / ✏️ Изменено
Оценка: 🔴 Критично / 🟠 Существенно / 🟡 Незначительно

### Рекомендации
Дай рекомендации по изменениям.
"""
                            
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "user", "content": compare_prompt}],
                                temperature=0.1
                            )
                            
                            comparison = response.choices[0].message.content
                            st.session_state.comparison_result = comparison
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Ошибка сравнения: {e}")
            else:
                # Показываем результат сравнения
                comp_res = st.session_state.comparison_result
                st.markdown(f"<div class='report-card'>{comp_res.strip()}</div>", unsafe_allow_html=True)
                
                st.write("")
                # Кнопки скачивания
                comp_col1, comp_col2, comp_col3 = st.columns(3)
                with comp_col1:
                    comp_pdf = create_pdf(comp_res)
                    if comp_pdf:
                        st.download_button("📥 PDF", data=bytes(comp_pdf), file_name="comparison_report.pdf", 
                                         mime="application/pdf", use_container_width=True, key="comp_dl_pdf")
                with comp_col2:
                    try:
                        comp_word = create_docx(comp_res)
                        if comp_word:
                            st.download_button("📝 Word", data=comp_word, file_name="comparison_report.docx",
                                             mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                             use_container_width=True, key="comp_dl_word")
                    except:
                        pass
                with comp_col3:
                    if st.button("🔄 Новое сравнение", use_container_width=True, key="btn_comp_reset"):
                        if "comparison_result" in st.session_state:
                            del st.session_state["comparison_result"]
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

# --- ВКЛАДКА ИСТОРИЯ ---
if tab_history is not None:
    with tab_history:
        st.write("### 📂 История аудитов")
        if supabase and st.session_state.auth_user:
            try:
                uid = st.session_state.auth_user.id
                audits_res = supabase.table("audits").select("*").eq("user_id", uid).eq("is_paid", True).order("created_at", desc=True).execute()
                audits = audits_res.data or []
                
                if not audits:
                    st.info("📭 У вас пока нет оплаченных аудитов. Сделайте первый анализ!")
                else:
                    st.markdown(f"<p style='color: var(--secondary-text);'>Найдено аудитов: {len(audits)}</p>", unsafe_allow_html=True)
                    
                    for i, audit in enumerate(audits):
                        created = audit.get("created_at", "")
                        try:
                            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                            date_str = dt.strftime("%d.%m.%Y %H:%M")
                        except:
                            date_str = created[:10] if created else "—"
                        
                        score_val = audit.get("risk_score", 5)
                        bar_c, bar_s, risk_t = get_risk_params(score_val)
                        
                        with st.expander(f"📄 {audit.get('file_name', 'Документ')} — {date_str} | Риск: {risk_t} ({score_val}/10)", expanded=False):
                            st.markdown(f"""
                                <div class="risk-meter-container">
                                    <div style="height:25px; width:{score_val*10}%; background:{bar_c}; 
                                    box-shadow: 0 2px 10px {bar_s}; border-radius:8px; 
                                    display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size: 12px;">
                                        {risk_t} ({score_val}/10)
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Собираем полный текст
                            full_text = ""
                            if audit.get("analysis_free"):
                                full_text += audit["analysis_free"]
                            if audit.get("analysis_paid"):
                                full_text += "\n\n" + audit["analysis_paid"]
                            if audit.get("protocol_table"):
                                full_text += "\n\n" + audit["protocol_table"]
                            
                            if full_text.strip():
                                st.markdown(f"<div class='report-card'>{full_text.strip()}</div>", unsafe_allow_html=True)
                                
                                st.write("")
                                h_col1, h_col2 = st.columns(2)
                                with h_col1:
                                    h_pdf = create_pdf(full_text)
                                    if h_pdf:
                                        st.download_button("📥 PDF", data=bytes(h_pdf), file_name=f"audit_{date_str}.pdf",
                                                         mime="application/pdf", use_container_width=True, key=f"hist_pdf_{i}")
                                with h_col2:
                                    try:
                                        h_word = create_docx(full_text)
                                        if h_word:
                                            st.download_button("📝 Word", data=h_word, file_name=f"audit_{date_str}.docx",
                                                             mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                                             use_container_width=True, key=f"hist_word_{i}")
                                    except:
                                        pass
                            else:
                                st.info("Текст отчёта не сохранён для этого аудита.")
            except Exception as e:
                st.error(f"Ошибка загрузки истории: {e}")
        else:
            st.info("Войдите в аккаунт для просмотра истории.")

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
