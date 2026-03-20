# -*- coding: utf-8 -*-
import streamlit as st
from openai import OpenAI
import re
import uuid
from supabase import create_client, Client  # Добавили импорт Supabase
from streamlit_cookies_controller import CookieController, RemoveEmptyElementContainer

# Импорты из локальных модулей
from ui.design import load_css, get_risk_params, sample_text
from utils.file_processing import extract_text_from_pdf
from core.intelligence import analyze_long_text, generate_analysis, compare_documents
from utils.export import create_pdf, create_docx
from core.auth import sign_up, sign_in, sign_out, get_user_profile

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="JurisClear AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ИНИЦИАЛИЗАЦИЯ ---
cookie_controller = CookieController()
RemoveEmptyElementContainer()

if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

# Загружаем дизайн
load_css()

# --- 4. ПОДКЛЮЧЕНИЕ API И БАЗЫ ДАННЫХ ---
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

@st.cache_resource
def get_supabase_client():
    try:
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets.get("SUPABASE_SERVICE_KEY") or st.secrets.get("SUPABASE_KEY")
        return create_client(url, key)
    except Exception as e:
        st.error(f"Ошибка подключения к Supabase: {e}. Проверьте secrets.toml")
        return None

client = get_openai_client()
supabase = get_supabase_client()

# --- 3. ИНИЦИАЛИЗАЦИЯ AUTH STATE ---
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_display_name' not in st.session_state:
    st.session_state.user_display_name = ""

# --- АВТОМАТИЧЕСКИЙ ВХОД ЧЕРЕЗ COOKIES ---
# Обрабатываем запись и удаление куки ДО использования (чтобы избежать прерывания от st.rerun)
if "new_tokens" in st.session_state:
    cookie_controller.set("supabase_access_token", st.session_state.new_tokens["access"])
    cookie_controller.set("supabase_refresh_token", st.session_state.new_tokens["refresh"])
    del st.session_state["new_tokens"]

if "new_guest_token" in st.session_state:
    cookie_controller.set("guest_session_id", st.session_state.new_guest_token)
    del st.session_state["new_guest_token"]

if "clear_tokens" in st.session_state:
    cookie_controller.remove("supabase_access_token")
    cookie_controller.remove("supabase_refresh_token")
    del st.session_state["clear_tokens"]

def load_active_analysis(profile):
    """Вспомогательная функция для загрузки сохраненного анализа в session_state"""
    if profile:
        if profile.get("active_analysis_result"):
            st.session_state.analysis_result = profile.get("active_analysis_result")
        if profile.get("active_audit_score") is not None:
            st.session_state.audit_score = profile.get("active_audit_score")
        if profile.get("active_role"):
            st.session_state[f"role_pills_{st.session_state.reset_counter}"] = profile.get("active_role")
        if profile.get("active_contract_type"):
            st.session_state[f"type_pills_{st.session_state.reset_counter}"] = profile.get("active_contract_type")

if supabase and not st.session_state.is_authenticated:
    access_token = cookie_controller.get("supabase_access_token")
    refresh_token = cookie_controller.get("supabase_refresh_token")
    if access_token and refresh_token:
        try:
            session_response = supabase.auth.set_session(access_token, refresh_token)
            if session_response and session_response.user:
                user = session_response.user
                st.session_state.is_authenticated = True
                st.session_state.user_email = user.email
                st.session_state.user_id = user.id
                
                profile = get_user_profile(supabase, user.id)
                display_name = (user.user_metadata or {}).get("display_name", "")
                if not display_name and profile:
                    display_name = profile.get("display_name", "")
                st.session_state.user_display_name = display_name
                
                load_active_analysis(profile)
                
                # Обновляем токены в куках (так как refresh_token мог примениться)
                if session_response.session:
                    st.session_state.new_tokens = {
                        "access": session_response.session.access_token,
                        "refresh": session_response.session.refresh_token
                    }
        except Exception as e:
            # Если токен истек или недействителен - просто очищаем куки
            st.session_state.clear_tokens = True

if not st.session_state.is_authenticated:
    current_guest_sess = cookie_controller.get("guest_session_id")
    if current_guest_sess and st.session_state.get("loaded_guest_session_id") != current_guest_sess:
        if supabase:
            try:
                res = supabase.table("guest_analyses").select("*").eq("session_id", current_guest_sess).execute()
                if res.data and len(res.data) > 0:
                    data = res.data[0]
                    if data.get("active_analysis_result"):
                        st.session_state.analysis_result = data.get("active_analysis_result")
                    if data.get("active_audit_score") is not None:
                        st.session_state.audit_score = data.get("active_audit_score")
                    if data.get("active_role"):
                        st.session_state[f"role_pills_{st.session_state.reset_counter}"] = data.get("active_role")
                    if data.get("active_contract_type"):
                        st.session_state[f"type_pills_{st.session_state.reset_counter}"] = data.get("active_contract_type")
                    # Восстанавливаем статус оплаты
                    if data.get("payment_status") == "paid":
                        st.session_state.guest_paid = True
            except Exception as e:
                pass
        st.session_state.loaded_guest_session_id = current_guest_sess


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
            if not email or not password:
                st.error("Заполните email и пароль.")
            elif supabase is None:
                st.error("Ошибка подключения к базе данных.")
            else:
                with st.spinner("Вход в систему..."):
                    response, error = sign_in(supabase, email, password)
                if error:
                    st.error(error)
                else:
                    user = response.user
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = user.email
                    st.session_state.user_id = user.id
                    # Получаем display_name из метаданных или профиля
                    profile = get_user_profile(supabase, user.id)
                    display_name = (user.user_metadata or {}).get("display_name", "")
                    if not display_name and profile:
                        display_name = profile.get("display_name", "")
                    st.session_state.user_display_name = display_name
                    
                    load_active_analysis(profile)
                    
                    # Сохраняем токены в session_state для записи в куки на следующем рендере
                    if response.session:
                        st.session_state.new_tokens = {
                            "access": response.session.access_token,
                            "refresh": response.session.refresh_token
                        }
                    
                    st.rerun()

    with tabs[1]:
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        reg_name = st.text_input("Имя", placeholder="Иван Иванов", key="reg_name")
        reg_email = st.text_input("Электронная почта", placeholder="example@mail.com", key="reg_email")
        reg_password = st.text_input("Пароль", type="password", placeholder="••••••••", key="reg_pass")
        
        if st.button("Создать аккаунт", use_container_width=True, type="primary"):
            if not reg_email or not reg_password:
                st.error("Заполните email и пароль.")
            elif len(reg_password) < 6:
                st.error("Пароль должен содержать минимум 6 символов.")
            elif supabase is None:
                st.error("Ошибка подключения к базе данных.")
            else:
                with st.spinner("Создание аккаунта..."):
                    response, error = sign_up(supabase, reg_email, reg_password, reg_name)
                if error:
                    st.error(error)
                else:
                    user = response.user
                    # Проверяем, нужно ли подтверждение email
                    if response.session:
                        # Email confirmation отключён - сразу входим
                        st.session_state.is_authenticated = True
                        st.session_state.user_email = user.email
                        st.session_state.user_id = user.id
                        st.session_state.user_display_name = reg_name
                        
                        # Сохраняем токены в session_state для записи в куки на следующем рендере
                        st.session_state.new_tokens = {
                            "access": response.session.access_token,
                            "refresh": response.session.refresh_token
                        }
                        
                        st.rerun()
                    else:
                        # Email confirmation включён
                        st.success("✅ Аккаунт создан! Проверьте почту для подтверждения email.")

    st.markdown("""
        <div class="auth-footer">
            Продолжая, вы соглашаетесь с нашими <br> 
            <a href='#' style='color: var(--accent-blue);'>Условиями использования</a>
        </div>
    """, unsafe_allow_html=True)

# Подключение к API и БД было перемещено выше, для корректной работы авто-логина

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
        # Профиль пользователя
        avatar_letter = (
            st.session_state.user_display_name[0].upper() 
            if st.session_state.user_display_name 
            else (st.session_state.user_email[0].upper() if st.session_state.user_email else "U")
        )
        cols = st.columns([1, 1.5])
        with cols[0]:
            st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: flex-end; height: 100%; margin-top: 5px;">
                    <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3); border: 1px solid rgba(255,255,255,0.2);">
                        {avatar_letter}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            if st.button("Выйти", use_container_width=True):
                # Очистка активного анализа в БД
                if st.session_state.is_authenticated and st.session_state.user_id and supabase:
                    try:
                        supabase.table("profiles").update({
                            "active_analysis_result": None,
                            "active_audit_score": None,
                            "active_role": None,
                            "active_contract_type": None
                        }).eq("id", st.session_state.user_id).execute()
                    except Exception as e:
                        pass
                        
                # Очистка анализа из session_state
                st.session_state.reset_counter += 1
                for k in ["analysis_result", "audit_score", "compare_result"]:
                    if k in st.session_state: 
                        del st.session_state[k]

                if supabase:
                    sign_out(supabase)
                st.session_state.clear_tokens = True
                if "loaded_guest_session_id" in st.session_state:
                    del st.session_state["loaded_guest_session_id"]
                st.session_state.is_authenticated = False
                st.session_state.user_email = ""
                st.session_state.user_id = None
                st.session_state.user_display_name = ""
                st.rerun()

st.markdown(f"<p style='text-align: center; color: var(--secondary-text); font-weight: 500;'>Профессиональный юридический аудит договоров</p>", unsafe_allow_html=True)

# --- ОБНОВЛЕННЫЕ ТАРИФЫ С КОНКРЕТНЫМИ ФУНКЦИЯМИ ---
col_tar1, col_tar2 = st.columns(2)

with col_tar1:
    st.markdown(f"""
        <div class="pricing-card-single">
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
            <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 30px;">
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 12px; text-align: center; font-size: 13px; font-weight: 500;">
                    ℹ️ Оплачивайте только если результат вас устроит
                </div>
                <button style="width: 100%; background: rgba(255,255,255,0.08); color: white; border: 1px solid rgba(255,255,255,0.1); padding: 12px; border-radius: 12px; font-weight: 600; cursor: default;">Анализ доступен ниже 👇</button>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_tar2:
    checkout_url = "https://jurisclearai.lemonsqueezy.com/checkout/buy/69a180c9-d5f5-4018-9dbe-b8ac64e4ced8"
    st.markdown(f"""
        <div class="pricing-card-pro">
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
            <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 30px;">
                <div style="background: rgba(157, 0, 255, 0.1); padding: 10px; border-radius: 12px; text-align: center; font-size: 13px; font-weight: 500;">
                    🔐 Для оформления подписки нужно зарегистрироваться
                </div>
                <div style="background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.5); text-align: center; padding: 12px; border-radius: 12px; font-weight: 700; font-size: 15px; border: 1px dashed rgba(255,255,255,0.2); cursor: not-allowed;">
                    🚀 Оформить подписку
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Параметры анализа
st.markdown("### ⚙️ Параметры анализа")

@st.fragment
def render_analysis_params():
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Ваша роль:**")
        st.pills(
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
        st.pills(
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

render_analysis_params()

# Функции для кэширования экспорта
@st.cache_data
def get_cached_pdf(content):
    return create_pdf(content)

@st.cache_data
def get_cached_docx(content):
    return create_docx(content)

# Рабочее пространство (Вкладки)
tab_audit, tab_demo, tab_compare = st.tabs(["🚀 ИИ Аудит", "📝 Пример отчета", "⚖️ Сравнение"])

with tab_audit:
    @st.fragment
    def render_audit_content():
        # Достаем значения из pills (они сохраняются в session_state по ключам)
        user_role = st.session_state.get(f"role_pills_{st.session_state.reset_counter}", "Заказчик")
        contract_type = st.session_state.get(f"type_pills_{st.session_state.reset_counter}", "Авто-определение")

        # --- ЮРИДИЧЕСКИЙ ДИСКЛЕЙМЕР ---
        st.markdown("""
            <div class="disclaimer-glass">
                <h4>⚖️ Внимание: Юридический отказ от ответственности</h4>
                <p>
                    Данный сервис работает на базе искусственного интеллекта и <b>не является юридической консультацией</b>. 
                    ИИ может ошибаться, галлюцинировать или пропускать важные детали. 
                    Результаты анализа носят ознакомительный характер. Перед принятием решений обязательно 
                    <b>проконсультируйтесь с квалифицированным юристом</b>. 
                    Мы не несем ответственности за последствия использования данного инструмента.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Если анализ уже есть в памяти, показываем его без загрузчика
        if "analysis_result" in st.session_state:
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

            st.success("✅ Анализ и протокол разногласий успешно сформированы!")
            clean_res = st.session_state.analysis_result
            
            # Определяем, оплачен ли анализ (для гостей)
            is_guest = not st.session_state.is_authenticated
            guest_paid = st.session_state.get("guest_paid", False)
            show_full = st.session_state.is_authenticated or guest_paid
            
            if show_full:
                # --- ПОЛНЫЙ ОТЧЕТ (после оплаты или для зарегистрированных) ---
                st.markdown(f"<div class='report-card'>{clean_res.strip()}</div>", unsafe_allow_html=True)
                
                st.write("")
                col_pdf, col_word = st.columns(2)
                with col_pdf:
                    pdf_bytes = get_cached_pdf(clean_res)
                    if pdf_bytes:
                        st.download_button(
                            label="📥 Скачать PDF",
                            data=bytes(pdf_bytes),
                            file_name="audit_report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="btn_download_pdf_audit"
                        )
                with col_word:
                    try:
                        word_bytes = get_cached_docx(clean_res)
                        if word_bytes:
                            st.download_button(
                                label="📝 Скачать Word",
                                data=word_bytes,
                                file_name="audit_report.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key="btn_download_docx_audit"
                            )
                    except Exception as e:
                        pass
            else:
                # --- ДЕМО-ВЕРСИЯ (разделённый отчет для неоплативших гостей) ---
                split_marker_1 = "3. РИСКИ РАСТОРЖЕНИЯ И СПОРОВ"
                split_marker_2 = "## 🛠️ Протокол разногласий"
                
                public_part = clean_res
                if split_marker_1 in clean_res:
                    public_part = clean_res.split(split_marker_1)[0]
                elif split_marker_2 in clean_res:
                    public_part = clean_res.split(split_marker_2)[0]
                
                st.markdown(f"<div class='report-card'>{public_part.strip()}</div>", unsafe_allow_html=True)
                
                # Визуальная заглушка для скрытой части
                st.markdown("""
                    <div style="position: relative; margin-top: -80px; height: 120px; background: linear-gradient(to bottom, transparent 0%, var(--background-color, #0e1117) 80%); display: flex; align-items: flex-end; justify-content: center; padding-bottom: 15px; z-index: 10;">
                        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 8px 16px; border-radius: 8px; backdrop-filter: blur(5px);">
                            <p style="color: var(--secondary-text); font-weight: 500; font-size: 14px; text-align: center; margin: 0;">
                                🔒 Полный анализ (риски расторжения и споров) и протокол разногласий скрыты
                            </p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                st.write("")
                
                # Кнопка покупки разового аудита с session_id
                guest_sess = cookie_controller.get("guest_session_id")
                if not guest_sess:
                    guest_sess = st.session_state.get("new_guest_token", "")
                
                buy_link = f"https://jurisclearai.lemonsqueezy.com/checkout/buy/0fb5f2af-1335-4dfd-9091-ea9aa9eb6303?checkout[custom][session_id]={guest_sess}"
                st.markdown(f"""
                    <a href='{buy_link}' target='_blank' style='text-decoration: none;'>
                        <div style='background: linear-gradient(135deg, #FF9933 0%, #FF6600 100%); color: white; padding: 14px; border-radius: 12px; text-align: center; font-weight: 700; font-size: 16px; width: 100%; box-shadow: 0 4px 15px rgba(255, 102, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.2); cursor: pointer; transition: transform 0.2s;'>
                            🛍️ Купить разовый аудит за 9$
                        </div>
                    </a>
                """, unsafe_allow_html=True)
                
                # --- AUTO-POLLING: проверка оплаты каждые 5 секунд ---
                if guest_sess:
                    check_url = f"https://zqcucvoeybuudpzxziqq.supabase.co/functions/v1/check-payment-status?session_id={guest_sess}"
                    st.markdown(f"""
                        <script>
                        (function() {{
                            var pollInterval = setInterval(function() {{
                                fetch("{check_url}")
                                    .then(function(resp) {{ return resp.json(); }})
                                    .then(function(data) {{
                                        if (data.paid === true) {{
                                            clearInterval(pollInterval);
                                            // Отправляем сигнал Streamlit перезагрузить страницу
                                            window.parent.location.reload();
                                        }}
                                    }})
                                    .catch(function(err) {{ console.log("Poll error:", err); }});
                            }}, 5000);
                        }})();
                        </script>
                    """, unsafe_allow_html=True)
                    
                    st.caption("⏳ После оплаты страница обновится автоматически")

            st.write("")
            if st.button("📁 Загрузить новый договор", use_container_width=True, key="btn_paid_reset"):
                st.session_state.reset_counter += 1
                keys_to_clear = ["analysis_result", "audit_score", "guest_paid"]
                for k in keys_to_clear:
                    if k in st.session_state: del st.session_state[k]
                    
                # Очистка в БД
                if st.session_state.is_authenticated and st.session_state.user_id and supabase:
                    try:
                        supabase.table("profiles").update({
                            "active_analysis_result": None,
                            "active_audit_score": None,
                            "active_role": None,
                            "active_contract_type": None
                        }).eq("id", st.session_state.user_id).execute()
                    except Exception as e:
                        pass
                elif not st.session_state.is_authenticated:
                    guest_sess = cookie_controller.get("guest_session_id")
                    if guest_sess and supabase:
                        try:
                            supabase.table("guest_analyses").delete().eq("session_id", guest_sess).execute()
                        except Exception as e:
                            pass
                        
                st.rerun()
        else:
            # Иначе показываем загрузчик
            file = st.file_uploader("Выберите файл договора (PDF)", type=['pdf'], key=f"uploader_{st.session_state.reset_counter}")
            
            if file:
                analyze_btn_placeholder = st.empty()
                if analyze_btn_placeholder.button("Начать анализ", use_container_width=True, type="primary"):
                    analyze_btn_placeholder.empty()
                    with st.spinner("ИИ проводит глубокий юридический аудит..."):
                        try:
                            file_bytes = file.read()
                            text = extract_text_from_pdf(file_bytes)

                            if not text.strip():
                                st.error("Не удалось извлечь текст из документа. Возможно, файл поврежден или пуст.")
                                st.stop()
                            
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
                            special_instructions = "Фокус на переходах рисков, соках поставки, штрафах за недопоставку и скрытых дефектах."
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

                        raw_res = analyze_long_text(client, text, contract_type, user_role, special_instructions, prompt_instruction)
                        
                        score_match = re.search(r"SCORE:\s*(\d+)", raw_res)
                        score = int(score_match.group(1)) if score_match else 5
                        clean_res = re.sub(r"SCORE:\s*\d+", "", raw_res).strip()

                        if clean_res:
                            st.session_state.analysis_result = clean_res
                            st.session_state.audit_score = score
                            
                            # Сохранение в БД
                            if st.session_state.is_authenticated and st.session_state.user_id and supabase:
                                try:
                                    supabase.table("profiles").update({
                                        "active_analysis_result": clean_res,
                                        "active_audit_score": score,
                                        "active_role": user_role,
                                        "active_contract_type": contract_type
                                    }).eq("id", st.session_state.user_id).execute()
                                except Exception as e:
                                    pass
                            elif not st.session_state.is_authenticated:
                                guest_sess = cookie_controller.get("guest_session_id")
                                if not guest_sess:
                                    guest_sess = str(uuid.uuid4())
                                    st.session_state.new_guest_token = guest_sess
                                
                                st.session_state.loaded_guest_session_id = guest_sess
                                
                                if supabase and guest_sess:
                                    try:
                                        guest_data = {
                                            "session_id": guest_sess,
                                            "active_analysis_result": clean_res,
                                            "active_audit_score": score,
                                            "active_role": user_role,
                                            "active_contract_type": contract_type
                                        }
                                        res = supabase.table("guest_analyses").select("id").eq("session_id", guest_sess).execute()
                                        if res.data and len(res.data) > 0:
                                            supabase.table("guest_analyses").update(guest_data).eq("session_id", guest_sess).execute()
                                        else:
                                            supabase.table("guest_analyses").insert(guest_data).execute()
                                    except Exception as e:
                                        pass
                                    
                            st.rerun()

    render_audit_content()

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

with tab_compare:
    @st.fragment
    def render_compare_content():
        if not st.session_state.is_authenticated:
            st.markdown(f"""
                <div style='text-align: center; padding: 40px; background: rgba(255, 255, 255, 0.05); border-radius: 12px; margin-top: 20px;'>
                    <div style='font-size: 40px; margin-bottom: 10px;'>🔒</div>
                    <h3>Инструмент сравнения доступен только для зарегистрированных пользователей</h3>
                    <p style='color: var(--secondary-text);'>Пожалуйста, войдите в систему или зарегистрируйтесь, чтобы использовать функцию ИИ-сравнения документов.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("### ⚖️ ИИ Сравнение документов")
            st.write("Загрузите оригинальную и измененную версии договора, чтобы найти юридически значимые изменения.")
            
            user_role_comp = st.session_state.get(f"role_pills_{st.session_state.reset_counter}", "Заказчик")
            contract_type_comp = st.session_state.get(f"type_pills_{st.session_state.reset_counter}", "Авто-определение")
            
            col_orig, col_rev = st.columns(2)
            with col_orig:
                file_orig = st.file_uploader("Оригинальный договор (PDF)", type=['pdf'], key=f"uploader_orig_{st.session_state.reset_counter}")
            with col_rev:
                file_rev = st.file_uploader("Измененный договор (PDF)", type=['pdf'], key=f"uploader_rev_{st.session_state.reset_counter}")
                
            if "compare_result" in st.session_state:
                st.success("✅ Сравнение успешно завершено!")
                st.markdown(f"<div class='report-card'>{st.session_state.compare_result.strip()}</div>", unsafe_allow_html=True)
                
                st.write("")
                col_pdf_comp, col_word_comp = st.columns(2)
                with col_pdf_comp:
                    pdf_bytes_comp = get_cached_pdf(st.session_state.compare_result)
                    if pdf_bytes_comp:
                        st.download_button(
                            label="📥 Скачать PDF",
                            data=bytes(pdf_bytes_comp),
                            file_name=f"comparison_report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="btn_download_pdf_comp"
                        )
                with col_word_comp:
                    try:
                        word_bytes_comp = get_cached_docx(st.session_state.compare_result)
                        if word_bytes_comp:
                            st.download_button(
                                label="📝 Скачать Word",
                                data=word_bytes_comp,
                                file_name=f"comparison_report.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key="btn_download_docx_comp"
                            )
                    except Exception as e:
                        pass
                st.write("")
                if st.button("📁 Загрузить другие документы", use_container_width=True, key="btn_reset_comp"):
                    del st.session_state["compare_result"]
                    st.session_state.reset_counter += 1
                    st.rerun(scope="fragment")
                    
            elif file_orig and file_rev:
                comp_btn_placeholder = st.empty()
                if comp_btn_placeholder.button("Начать сравнение", use_container_width=True, type="primary"):
                    comp_btn_placeholder.empty()
                    with st.spinner("ИИ анализирует различия..."):
                        try:
                            text_orig = extract_text_from_pdf(file_orig.read())
                            text_rev = extract_text_from_pdf(file_rev.read())
                            
                            if not text_orig.strip() or not text_rev.strip():
                                st.error("Не удалось извлечь текст из одного или обоих документов.")
                                st.stop()
                                
                        except Exception as e:
                            st.error(f"Ошибка при чтении PDF: {e}")
                            st.stop()
                            
                        res = compare_documents(client, text_orig, text_rev, contract_type_comp, user_role_comp)
                        if res:
                            st.session_state.compare_result = res
                            st.rerun(scope="fragment")

    render_compare_content()

st.divider()
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption("© 2026 JurisClear AI | Ереван")

st.markdown(f"<p style='text-align: center; color: var(--secondary-text); font-size: 11px; margin-top: 20px;'>support@jurisclear.com</p>", unsafe_allow_html=True)
