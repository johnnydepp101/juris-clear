import streamlit as st

def load_css():
    st.markdown("""
    <style>
    /* 1. ПЕРЕМЕННЫЕ ПО УМОЛЧАНИЮ (DARK THEME) */
    /* 0. ПОДКЛЮЧЕНИЕ ШРИФТОВ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-color: #0d1117;
        --card-bg: rgba(30, 41, 59, 0.45);
        --text-color: #e2e8f0; /* Более мягкий белый */
        --secondary-text: #94a3b8;
        --border-color: rgba(255, 255, 255, 0.06);
        --accent-blue: #6366f1; /* Переходим на Indigo для мягкости */
        --accent-green: #10b981;
        --glass-blur: blur(20px);
        --card-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5);
        --header-color: #f8fafc;
        --font-main: 'Inter', sans-serif;
        --font-header: 'Outfit', sans-serif;
        --mesh-opacity: 0.15;
    }

    /* 2. АВТОМАТИЧЕСКАЯ СВЕТЛАЯ ТЕМА */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-color: #f1f5f9; /* Мягкий светло-серый */
            --card-bg: rgba(255, 255, 255, 0.8);
            --text-color: #1e293b;
            --secondary-text: #64748b;
            --border-color: rgba(0, 0, 0, 0.08);
            --card-shadow: 0 10px 40px -10px rgba(31, 38, 135, 0.1);
            --header-color: #0f172a;
            --mesh-opacity: 0.25;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(241, 245, 249, 0.95) 100%) !important;
        }
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    .block-container {
        padding-top: 2rem; 
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* ГЛОБАЛЬНЫЕ СТИЛИ */
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-color);
        /* Анимированный Mesh + Тонкая Сетка */
        background-image: 
            linear-gradient(var(--border-color) 1px, transparent 1px),
            linear-gradient(90deg, var(--border-color) 1px, transparent 1px),
            radial-gradient(at 10% 10%, rgba(99, 102, 241, var(--mesh-opacity)) 0px, transparent 50%),
            radial-gradient(at 90% 10%, rgba(16, 185, 129, calc(var(--mesh-opacity) * 0.7)) 0px, transparent 50%),
            radial-gradient(at 50% 90%, rgba(99, 102, 241, calc(var(--mesh-opacity) * 0.8)) 0px, transparent 50%);
        background-size: 40px 40px, 40px 40px, 150% 150%, 150% 150%, 150% 150%;
        background-attachment: fixed;
        animation: mesh-gradient 25s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        color: var(--text-color);
        font-family: var(--font-main);
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes mesh-gradient {
        0% { background-position: 0% 0%; }
        50% { background-position: 100% 100%; }
        100% { background-position: 0% 0%; }
    }

    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: var(--font-header) !important;
        letter-spacing: -0.02em !important;
    }

    /* УБИРАЕМ ЯКОРЯ */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, 
    .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a { display: none !important; }
    [data-testid="stMarkdownHeader"] a { display: none !important; }

    /* ХЕДЕР И ВЫРАВНИВАНИЕ */
    [data-testid="stHorizontalBlock"] { align-items: center !important; }

    /* ТАРИФНЫЕ КАРТОЧКИ (ОБНОВЛЕННЫЕ) */
    .pricing-card-base {
        display: flex; 
        flex-direction: column; 
        justify-content: space-between; 
        padding: 30px; 
        border-radius: 20px; 
        height: 440px; 
        color: var(--text-color);
        backdrop-filter: var(--glass-blur);
        border: 1px solid var(--border-color);
        box-shadow: var(--card-shadow);
        transition: all 0.4s ease;
    }
    
    .pricing-card-1 {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(30, 41, 59, 0.4) 100%);
    }
    
    .pricing-card-2 {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
    }

    .pricing-card-base:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.4);
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
        background-blend-mode: overlay;
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
        margin-bottom: 35px;
    }
    
    /* ШКАЛА РИСКА */
    .risk-meter-container {
        background: rgba(0, 0, 0, 0.03); 
        border-radius: 24px; padding: 12px;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.05); 
        border: 1px solid var(--border-color); 
        margin: 25px 0;
    }

    /* GLASS PANEL / CONTAINER (Parameters & Sections) */
    /* Используем максимально широкий и мощный селектор для всех контейнеров с рамкой */
    div[data-testid="stVerticalBlockBorderWrapper"], 
    div[data-testid="stVerticalBlock"], 
    .glass-panel, 
    .st-key-analysis_params {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        background-color: #1e293b !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 22px !important;
        padding: 25px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6) !important;
        margin-bottom: 30px !important;
    }
    
    /* Убираем прозрачность у вложенных элементов Streamlit, которые могут перекрывать фон */
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    div[data-testid="stVerticalBlock"] > div {
        background-color: transparent !important;
    }
    
    /* ЮРИДИЧЕСКИЙ ДИСКЛЕЙМЕР (Elite Style) */
    .legal-disclaimer {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        padding: 20px !important;
        border-radius: 16px !important;
        margin-bottom: 25px !important;
        backdrop-filter: blur(12px) !important;
    }
    
    .legal-disclaimer h4 {
        color: #ef4444 !important;
        margin-top: 0 !important;
        font-weight: 700 !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* ЭЛЕМЕНТЫ ВВОДА (Streamlit) */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
        background-color: var(--card-bg) !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15), inset 0 2px 4px rgba(0,0,0,0.05) !important;
        background-color: rgba(30, 41, 59, 0.6) !important;
    }

    /* КНОПКИ */
    .stButton > button {
        border-radius: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        font-size: 14px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 15px -5px rgba(99, 102, 241, 0.4) !important;
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 25px -5px rgba(99, 102, 241, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
    }

    .stLinkButton > a {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    .stDownloadButton > button:hover {
        border: 1px solid var(--accent-blue) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* КАСТОМНЫЙ СКРОЛЛБАР */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.3);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.5);
    }

    /* АНИМАЦИЯ ПОЯВЛЕНИЯ */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* КАРТОЧКА ОТЧЕТА */
    .report-card {
        animation: fadeInUp 0.6s ease-out forwards;
        background-color: var(--card-bg);
        backdrop-filter: var(--glass-blur);
        border-left: 6px solid var(--accent-blue);
        padding: 30px; border-radius: 16px; 
        margin-top: 25px; color: var(--text-color);
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
        box-shadow: var(--card-shadow);
        margin-bottom: 35px;
    }

    /* СТИЛИ ДЛЯ МОДАЛЬНОГО ОКНА АВТОРИЗАЦИИ */
    [data-testid="stDialog"] {
        border-radius: 24px !important;
        background: var(--bg-color) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    [data-testid="stDialog"] h2 {
        color: var(--header-color) !important;
        font-weight: 800 !important;
    }

    .auth-footer {
        text-align: center;
        margin-top: 25px;
        font-size: 12px;
        color: var(--secondary-text);
        opacity: 0.7;
    }
    /* МАЛЕНЬКИЕ УЛУЧШЕНИЯ ТИПОГРАФИКИ */
    .secondary-text {
        color: var(--secondary-text);
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    /* ТАБЫ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0 !important;
        padding: 10px 20px !important;
        color: var(--secondary-text) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--card-bg) !important;
        color: var(--accent-blue) !important;
        backdrop-filter: var(--glass-blur);
    }

    /* АНИМАЦИЯ ДЛЯ КНОПОК */
    @keyframes pulse-blue {
        0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
        100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
    }
    
    .login-btn-header {
        animation: pulse-blue 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

def get_risk_params(score):
    if score <= 3:
        return "linear-gradient(90deg, #059669 0%, #10b981 100%)", "rgba(16, 185, 129, 0.5)", "НИЗКИЙ"
    elif score <= 6:
        return "linear-gradient(90deg, #d97706 0%, #fbbf24 100%)", "rgba(251, 191, 36, 0.5)", "СРЕДНИЙ"
    else:
        return "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)", "rgba(239, 68, 68, 0.5)", "КРИТИЧЕСКИЙ"

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
