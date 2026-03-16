import streamlit as st

def load_css():
    st.markdown("""
    <style>
    /* 1. ПЕРЕМЕННЫЕ ПО УМОЛЧАНИЮ (DARK THEME) */
    :root {
        --bg-color: #01010a;
        --card-bg: rgba(255, 255, 255, 0.03); /* Ультра-прозрачный белый для эффекта стекла */
        --text-color: #f0f6fc;
        --secondary-text: #8b949e;
        --border-color: rgba(255, 255, 255, 0.12); /* Чуть более заметная граница для блика */
        --accent-blue: #3b82f6;
        --accent-green: #10b981;
        --glass-blur: blur(25px); /* Усиленное размытие как на картинке */
        --card-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        --header-color: #ffffff;
        
        /* Цвета для точного воссоздания картинки */
        --bg-grad-vibrant: #190e20;
        --bg-grad-deep: #05053a;
        --bg-grad-dark: #01010a;
    }

    /* 2. АВТОМАТИЧЕСКАЯ СВЕТЛАЯ ТЕМА (ПО НАСТРОЙКАМ СИСТЕМЫ) */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-color: #f8f9fc;
            --card-bg: rgba(255, 255, 255, 0.7);
            --text-color: #0f172a;
            --secondary-text: #475569;
            --border-color: rgba(0, 0, 0, 0.1);
            --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
            --header-color: #01010a;

            /* Цвета фона для светлого режима (на основе новой картинки) */
            --bg-grad-vibrant: #ffb2ef; /* Розовое пятно */
            --bg-grad-deep: #5c67ff;    /* Синее пятно */
            --bg-grad-dark: #ffffff;
        }

        /* ГРАДИЕНТНЫЙ ФОН КАРТОЧЕК КАК НА КАРТИНКЕ */
        .pricing-card-single, .pricing-card-pro, .report-card {
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.35) 0%, rgba(100, 110, 255, 0.25) 100%), 
                        rgba(255, 255, 255, 0.5) !important;
            backdrop-filter: blur(30px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(30px) saturate(160%) !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            box-shadow: 0 15px 45px rgba(0, 0, 0, 0.05) !important;
            color: #1e293b !important;
        }

        /* Полная замена белого текста на темный во всех элементах */
        .pricing-card-single *, .pricing-card-pro *, .report-card *, 
        .stMarkdown div p, .stMarkdown div span, .stMarkdown div b,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #1e293b !important;
        }

        .pricing-card-pro {
            border: 1.5px solid rgba(157, 0, 255, 0.3) !important;
            background: linear-gradient(135deg, rgba(255, 150, 240, 0.45) 0%, rgba(100, 110, 255, 0.3) 100%), 
                        rgba(255, 255, 255, 0.4) !important;
        }
            /* ВКЛАДКИ (TABS) В СВЕТЛОМ РЕЖИМЕ - ТЕМНЫЙ ТЕКСТ ВЕЗДЕ */
        .stTabs [data-baseweb="tab"] {
            color: #475569 !important;
            font-weight: 600 !important;
            background: transparent !important;
            border: none !important;
        }

        .stTabs [aria-selected="true"], .stTabs [aria-selected="true"] * {
            color: #01010a !important; /* ТЕМНЫЙ ТЕКСТ ДЛЯ АКТИВНОЙ ВКЛАДКИ */
            font-weight: 900 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: rgba(79, 70, 229, 0.1) !important; /* Светлый фон */
            border-radius: 12px 12px 0 0 !important;
        }

        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #4f46e5 !important;
            height: 3px !important;
        }

        /* ПИЛЮЛИ (PILLS) В СВЕТЛОМ РЕЖИМЕ - ТЕМНЫЙ ТЕКСТ ДЛЯ АКТИВНЫХ */
        [data-testid="stPill"][aria-selected="true"] {
            background: rgba(79, 70, 229, 0.15) !important; /* Светлый активный фон */
            border: 2px solid #4f46e5 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1) !important;
        }

        [data-testid="stPill"][aria-selected="true"] *, [data-testid="stPill"][aria-selected="true"] p {
            color: #01010a !important; /* ТЕМНЫЙ ТЕКСТ */
            font-weight: 800 !important;
        }

        /* КНОПКИ - ТЕМНЫЕ ДЛЯ КОНТРАСТА */
        .stButton > button, .login-btn-header button {
            color: #ffffff !important;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            border: none !important;
            box-shadow: 0 5px 15px rgba(79, 70, 229, 0.3) !important;
        }

        /* КНОПКА СКАЧИВАНИЯ В СВЕТЛОМ РЕЖИМЕ (В СТИЛЕ КАРТОЧЕК) */
        .stDownloadButton > button {
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.4) 0%, rgba(100, 110, 255, 0.3) 100%), 
                        rgba(255, 255, 255, 0.6) !important;
            color: #01010a !important; /* ТЕМНО-ЧЕРНЫЙ ТЕКСТ */
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(15px) !important;
            border-radius: 20px !important;
            padding: 14px 28px !important;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05) !important;
            font-weight: 800 !important; /* Более жирный шрифт */
        }

        .stDownloadButton > button:hover {
            transform: translateY(-2px) !important;
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.5) 0%, rgba(100, 110, 255, 0.4) 100%) !important;
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.08) !important;
            color: #000000 !important;
        }

        /* ИНПУТЫ И ПИЛЮЛИ (ОБЩЕЕ) */
        .stTextInput input, [data-testid="stPill"], .stTextArea textarea {
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: #1e293b !important;
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
        }
    
        [aria-selected="true"] {
            background: #4f46e5 !important;
            color: #ffffff !important;
        }

        [aria-selected="true"] div p {
            color: #ffffff !important;
        }

        /* ИНПУТЫ */
        .stTextInput input, .stTextArea textarea {
            background-color: #ffffff !important;
            color: #01010a !important;
            border: 1.5px solid rgba(0, 0, 0, 0.1) !important;
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
    
    /* ГЛОБАЛЬНЫЕ СТИЛИ ФОНА */
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-color) !important;
        background-image: 
            radial-gradient(at 85% 15%, var(--bg-grad-vibrant) 0%, transparent 60%), /* Розовое пятно сверху справа */
            radial-gradient(at 15% 85%, var(--bg-grad-deep) 0%, transparent 60%),    /* Синее пятно снизу слева */
            radial-gradient(at 50% 50%, var(--bg-grad-dark) 0%, transparent 100%) !important;
        background-attachment: fixed !important;
        background-size: cover !important;
        color: var(--text-color);
        transition: all 0.4s ease;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* УЛУЧШЕНИЕ ЧИТАЕМОСТИ В СВЕТЛОМ РЕЖИМЕ */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-color: #ffffff;
            --bg-grad-vibrant: rgba(255, 120, 240, 0.4); /* Насыщенный розовый */
            --bg-grad-deep: rgba(100, 110, 255, 0.4);    /* Насыщенный синий */
            --bg-grad-dark: #ffffff;
            --text-color: #01010a;
            --header-color: #01010a;
        }
        
        /* Гарантия видимости градиентов в светлом режиме */
        [data-testid="stAppViewContainer"] {
            background-image: 
                radial-gradient(at 85% 15%, rgba(255, 120, 240, 0.45) 0%, transparent 50%),
                radial-gradient(at 15% 85%, rgba(100, 110, 255, 0.45) 0%, transparent 50%),
                linear-gradient(to bottom, #ffffff, #f0f2f6) !important;
        }
    }

    /* УБИРАЕМ ЯКОРЯ */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, 
    .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a { display: none !important; }
    [data-testid="stMarkdownHeader"] a { display: none !important; }

    /* ХЕДЕР И ВЫРАВНИВАНИЕ */
    [data-testid="stHorizontalBlock"] { align-items: center !important; }

    /* ПРЕМИАЛЬНЫЕ ТАРИФНЫЕ КАРТОЧКИ (GLASSMORPHISM) */
    .pricing-card-single, .pricing-card-pro {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 450px;
        backdrop-filter: blur(35px) saturate(180%);
        -webkit-backdrop-filter: blur(35px) saturate(180%);
        padding: 40px; border-radius: 50px; 
        text-align: center; color: white;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .pricing-card-single {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 
                    inset 0 0 30px rgba(255, 255, 255, 0.03);
    }
    
    .pricing-card-pro {
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.08) 0%, rgba(157, 0, 255, 0.02) 100%);
        border: 1px solid rgba(157, 0, 255, 0.4);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 
                    0 0 40px rgba(157, 0, 255, 0.15),
                    inset 0 0 30px rgba(157, 0, 255, 0.05);
    }
    
    /* ЭФФЕКТ СВЕТА ВНУТРИ СТЕКЛА */
    .pricing-card-single::before, .pricing-card-pro::before {
        content: "";
        position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle at center, rgba(255, 255, 255, 0.05) 0%, transparent 40%);
        pointer-events: none;
        z-index: 0;
    }
    
    .pricing-card-pro::after {
        content: "";
        position: absolute;
        bottom: -20%; right: -10%; width: 60%; height: 60%;
        background: radial-gradient(circle at center, rgba(157, 0, 255, 0.2) 0%, transparent 70%);
        filter: blur(20px);
        pointer-events: none;
        z-index: 0;
    }

    /* Обеспечиваем, чтобы контент был выше слоев света */
    .pricing-card-single > div, .pricing-card-pro > div {
        position: relative;
        z-index: 2;
    }
    
    .pricing-card-single:hover, .pricing-card-pro:hover {
        transform: translateY(-12px) scale(1.02);
        border-color: rgba(157, 0, 255, 1);
        background: rgba(157, 0, 255, 0.05);
    }
    
    /* КАРТОЧКА ОТЧЕТА (FROSTED GLASS) */
    .report-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(40px) saturate(150%);
        -webkit-backdrop-filter: blur(40px) saturate(150%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 40px; border-radius: 40px; 
        margin-top: 25px; color: var(--text-color);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        margin-bottom: 35px;
        position: relative;
    }
    
    /* ШКАЛА РИСКА */
    .risk-meter-container {
        background: rgba(0, 0, 0, 0.2); 
        border-radius: 20px; padding: 10px;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.3); 
        border: 1px solid var(--border-color); 
        margin: 20px 0;
    }
    
    /* КНОПКИ (GLASSMORPHISM + NEON) */
    .stButton > button, .login-btn-header button {
        border-radius: 20px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        font-size: 13px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(157, 0, 255, 0.4) !important;
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%) !important;
        backdrop-filter: blur(10px) !important;
        color: white !important;
        padding: 14px 28px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }

    .stButton > button:hover, .login-btn-header button:hover {
        box-shadow: 0 0 25px rgba(157, 0, 255, 0.5) !important;
        border: 1px solid rgba(157, 0, 255, 1) !important;
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.4) 0%, rgba(59, 130, 246, 0.4) 100%) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
        padding: 14px 28px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        border: 1px solid rgba(157, 0, 255, 0.5) !important;
        box-shadow: 0 0 25px rgba(157, 0, 255, 0.3) !important;
        transform: translateY(-2px) !important;
    }

    /* СПЕЦИАЛЬНЫЙ СТИЛЬ ДЛЯ КНОПКИ ВХОДА В ХЕДЕРЕ */
    .login-btn-header button {
        background: rgba(157, 0, 255, 0.15) !important;
        border: 1px solid rgba(157, 0, 255, 0.6) !important;
        box-shadow: 0 0 15px rgba(157, 0, 255, 0.2) !important;
    }

    @keyframes pulse-neon {
        0% { box-shadow: 0 0 5px rgba(157, 0, 255, 0.4); }
        50% { box-shadow: 0 0 20px rgba(157, 0, 255, 0.2); }
        100% { box-shadow: 0 0 5px rgba(157, 0, 255, 0.4); }
    }
    
    .login-btn-header {
        animation: pulse-neon 3s infinite;
    }
    
    /* СТИЛИ ДЛЯ ТАБЛИЦ В ОТЧЕТЕ */
    .report-card table {
        margin-top: 25px !important;
        margin-bottom: 40px !important;
        border-collapse: collapse;
        width: 100%;
    }

    /* ЮРИДИЧЕСКИЙ ДИСКЛЕЙМЕР (RED GLASS) */
    .disclaimer-glass {
        background: rgba(255, 75, 75, 0.08);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 75, 75, 0.4);
        padding: 30px; border-radius: 30px; 
        margin-bottom: 30px;
        box-shadow: 0 15px 35px rgba(255, 75, 75, 0.1);
        position: relative;
        overflow: hidden;
    }

    .disclaimer-glass::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 6px; height: 100%;
        background: #ff4b4b;
    }

    .disclaimer-glass h4 {
        color: #ff4b4b !important;
        margin-top: 0 !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-size: 1.1rem !important;
    }

    .disclaimer-glass p {
        color: var(--text-color) !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        margin-bottom: 0 !important;
        opacity: 0.9;
    }

    .disclaimer-glass b {
        color: #ff4b4b !important;
        font-weight: 700;
    }

    /* МАЛЕНЬКИЕ УЛУЧШЕНИЯ ТИПОГРАФИКИ */
    .secondary-text {
        color: var(--secondary-text);
        font-size: 0.9rem;
    }

    /* СТИЛИ ДЛЯ ПИЛЮЛЬ (st.pills) - GLASSMORPHISM */
    [data-testid="stPill"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(5px) !important;
    }

    [data-testid="stPill"]:hover {
        background: rgba(157, 0, 255, 0.1) !important;
        border-color: rgba(157, 0, 255, 0.4) !important;
        transform: translateY(-2px);
    }

    /* Выбранная пилюля */
    [data-testid="stPill"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.4) 0%, rgba(59, 130, 246, 0.4) 100%) !important;
        border: 1px solid rgba(157, 0, 255, 1) !important;
        box-shadow: 0 0 15px rgba(157, 0, 255, 0.4) !important;
        color: white !important;
    }

    /* Текст внутри пилюль */
    [data-testid="stPill"] div p {
        color: var(--text-color) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stPill"][aria-selected="true"] div p {
        color: white !important;
        font-weight: 700 !important;
    }

    /* Заголовки пилюль */
    .stMarkdown p strong {
        color: var(--header-color);
        opacity: 0.9;
        letter-spacing: 0.5px;
    }
    
    /* СТИЛИ ДЛЯ МОДАЛЬНОГО ОКНА АВТОРИЗАЦИИ */
    [data-testid="stDialog"] {
        border-radius: 40px !important;
        background: rgba(1, 1, 10, 0.8) !important;
        backdrop-filter: blur(40px) !important;
        border: 1px solid rgba(157, 0, 255, 0.3) !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.8) !important;
    }
    
    [data-testid="stDialog"] h2 {
        color: var(--header-color) !important;
        font-weight: 800 !important;
        text-align: center;
    }

    /* Вкладки в модальном окне */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px 12px 0 0 !important;
        color: var(--secondary-text) !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(157, 0, 255, 0.1) !important;
        border-color: rgba(157, 0, 255, 0.6) !important;
        color: white !important;
    }

    .auth-footer {
        text-align: center;
        margin-top: 25px;
        font-size: 12px;
        color: var(--secondary-text);
        opacity: 0.7;
    }

    /* АНИМАЦИЯ ДЛЯ КНОПОК */
    @keyframes pulse-neon {
        0% { box-shadow: 0 0 5px rgba(157, 0, 255, 0.4); }
        50% { box-shadow: 0 0 20px rgba(157, 0, 255, 0.2); }
        100% { box-shadow: 0 0 5px rgba(157, 0, 255, 0.4); }
    }
    
    .login-btn-header {
        animation: pulse-neon 3s infinite;
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
