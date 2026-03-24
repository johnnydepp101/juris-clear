import streamlit as st

@st.cache_data
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

    /* ГЛОБАЛЬНАЯ TOUCH-ОПТИМИЗАЦИЯ */
    * {
        -webkit-tap-highlight-color: transparent;
        -webkit-text-size-adjust: 100%;
    }

    html {
        scroll-behavior: smooth;
        overscroll-behavior: none;
        touch-action: manipulation;
    }

    body {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
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

        /* КНОПКА СКАЧИВАНИЯ В СВЕТЛОМ РЕЖИМЕ - ТОТАЛЬНЫЙ ТЕМНЫЙ ТЕКСТ */
        [data-testid="stDownloadButton"] button, 
        [data-testid="stDownloadButton"] button *,
        .stDownloadButton > button, 
        .stDownloadButton > button * {
            color: #01010a !important;
            font-weight: 900 !important;
            text-decoration: none !important;
        }

        .stDownloadButton > button {
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.45) 0%, rgba(100, 110, 255, 0.35) 100%), 
                        rgba(255, 255, 255, 0.6) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(20px) !important;
            border-radius: 20px !important;
            padding: 14px 28px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.3s ease-in-out !important;
        }

        .stDownloadButton > button:hover {
            transform: translateY(-3px) !important;
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.55) 0%, rgba(100, 110, 255, 0.45) 100%) !important;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1) !important;
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
        padding-top: 1rem; 
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
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
        display: block;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        max-width: 100%;
    }

    /* OVERFLOW ДЛЯ ВСЕХ DATAFRAME И TABLE КОМПОНЕНТОВ */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        max-width: 100% !important;
    }

    [data-testid="stDataFrame"] > div {
        overflow-x: auto !important;
    }

    /* ПРЕДОТВРАЩЕНИЕ AUTO-ZOOM НА iOS ПРИ ФОКУСЕ НА INPUT */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select {
        font-size: 16px !important;
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

    /* ========== ЛИЧНЫЙ КАБИНЕТ ========== */

    /* Контейнер кабинета */
    .cabinet-container {
        max-width: 1100px;
        margin: 0 auto;
        padding: 10px 0;
    }

    /* Хедер кабинета с кнопкой назад */
    .cabinet-header {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .cabinet-header h2 {
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa 0%, #6366f1 50%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .cabinet-back-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        color: var(--text-color);
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        text-decoration: none;
    }

    .cabinet-back-btn:hover {
        background: rgba(157, 0, 255, 0.1);
        border-color: rgba(157, 0, 255, 0.4);
        transform: translateX(-3px);
    }

    /* Стеклянная карточка секции */
    .cabinet-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(30px) saturate(150%);
        -webkit-backdrop-filter: blur(30px) saturate(150%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .cabinet-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(157, 0, 255, 0.3), transparent);
    }

    .cabinet-card:hover {
        border-color: rgba(157, 0, 255, 0.15);
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
    }

    .cabinet-card-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 20px;
        color: var(--text-color);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Профиль: большой аватар */
    .profile-avatar-large {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        font-weight: 800;
        color: white;
        margin: 0 auto 20px;
        position: relative;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }

    .profile-avatar-large:hover {
        transform: scale(1.05);
    }

    .profile-avatar-badge {
        position: absolute;
        bottom: -4px;
        right: -4px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        font-size: 11px;
        font-weight: 900;
        padding: 3px 8px;
        border-radius: 8px;
        letter-spacing: 0.5px;
        box-shadow: 0 3px 10px rgba(16, 185, 129, 0.5);
    }

    /* Поле профиля */
    .profile-field {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }

    .profile-field:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(157, 0, 255, 0.2);
    }

    .profile-field-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--secondary-text);
        margin-bottom: 4px;
    }

    .profile-field-value {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-color);
    }

    .profile-field-action {
        padding: 8px 16px;
        background: rgba(157, 0, 255, 0.1);
        border: 1px solid rgba(157, 0, 255, 0.3);
        border-radius: 10px;
        color: #a78bfa;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        white-space: nowrap;
    }

    .profile-field-action:hover {
        background: rgba(157, 0, 255, 0.2);
        border-color: rgba(157, 0, 255, 0.6);
        transform: translateY(-1px);
    }

    /* Таблица истории */
    .history-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 18px 22px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }

    .history-row:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(157, 0, 255, 0.2);
        transform: translateX(4px);
    }

    .history-row-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .history-row-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-color);
    }

    .history-row-meta {
        font-size: 12px;
        color: var(--secondary-text);
    }

    .history-row-score {
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }

    .score-low { background: rgba(16, 185, 129, 0.15); color: #10b981; }
    .score-medium { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
    .score-high { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

    .history-row-actions {
        display: flex;
        gap: 8px;
    }

    .history-action-btn {
        padding: 6px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: var(--secondary-text);
        font-size: 13px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .history-action-btn:hover {
        background: rgba(157, 0, 255, 0.1);
        border-color: rgba(157, 0, 255, 0.3);
        color: #a78bfa;
    }

    /* Карточка биллинга */
    .billing-status-card {
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.08) 0%, rgba(59, 130, 246, 0.05) 100%);
        border: 1px solid rgba(157, 0, 255, 0.2);
        border-radius: 20px;
        padding: 28px;
        text-align: center;
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }

    .billing-status-card::after {
        content: "";
        position: absolute;
        bottom: -30%; right: -15%;
        width: 50%; height: 60%;
        background: radial-gradient(circle, rgba(157, 0, 255, 0.12) 0%, transparent 70%);
        filter: blur(15px);
        pointer-events: none;
    }

    .billing-status-active {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 20px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 30px;
        color: #10b981;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .billing-status-cancelled {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 20px;
        background: rgba(255, 75, 75, 0.15);
        border: 1px solid rgba(255, 75, 75, 0.3);
        border-radius: 30px;
        color: #ff6b6b;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .billing-info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        margin-top: 16px;
    }

    .billing-info-item {
        background: rgba(255, 255, 255, 0.04);
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .billing-info-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--secondary-text);
        margin-bottom: 6px;
    }

    .billing-info-value {
        font-size: 18px;
        font-weight: 800;
        color: var(--text-color);
    }

    /* Уведомления */
    .notification-card {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 18px 22px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
        position: relative;
    }

    .notification-card:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(157, 0, 255, 0.15);
    }

    .notification-card.unread {
        border-left: 3px solid #6366f1;
        background: rgba(99, 102, 241, 0.04);
    }

    .notification-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }

    .notification-icon.info { background: rgba(59, 130, 246, 0.15); }
    .notification-icon.success { background: rgba(16, 185, 129, 0.15); }
    .notification-icon.warning { background: rgba(251, 191, 36, 0.15); }
    .notification-icon.system { background: rgba(157, 0, 255, 0.15); }

    .notification-content {
        flex: 1;
    }

    .notification-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 4px;
    }

    .notification-text {
        font-size: 13px;
        color: var(--secondary-text);
        line-height: 1.5;
    }

    .notification-time {
        font-size: 11px;
        color: var(--secondary-text);
        opacity: 0.7;
        white-space: nowrap;
    }

    /* Заблокированная секция */
    .locked-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 30px;
        text-align: center;
        background: rgba(255, 255, 255, 0.02);
        border: 1px dashed rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        margin-top: 10px;
    }

    .locked-section-icon {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.6;
    }

    .locked-section-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 8px;
    }

    .locked-section-text {
        font-size: 14px;
        color: var(--secondary-text);
        max-width: 400px;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    .locked-section-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 28px;
        background: linear-gradient(135deg, #9d00ff 0%, #6366f1 100%);
        color: white;
        border-radius: 14px;
        font-size: 14px;
        font-weight: 700;
        text-decoration: none;
        box-shadow: 0 6px 20px rgba(157, 0, 255, 0.35);
        transition: all 0.3s ease;
    }

    .locked-section-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(157, 0, 255, 0.45);
    }

    /* Кнопка удаления аккаунта */
    .danger-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 14px;
        color: #ef4444;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .danger-btn:hover {
        background: rgba(239, 68, 68, 0.15);
        border-color: rgba(239, 68, 68, 0.5);
    }

    /* Кнопка cancel подписки стилизация */
    .cancel-sub-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        padding: 14px 24px;
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 14px;
        color: #ff6b6b;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
    }

    .cancel-sub-btn:hover {
        background: rgba(239, 68, 68, 0.15);
        border-color: rgba(239, 68, 68, 0.5);
        color: #ff4b4b;
    }

    /* Кнопка-ссылка для продления подписки */
    .renew-sub-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        padding: 14px 24px;
        background: linear-gradient(135deg, #9d00ff 0%, #6366f1 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 14px;
        color: white;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(157, 0, 255, 0.35);
        transition: all 0.3s ease;
        text-decoration: none;
    }

    .renew-sub-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(157, 0, 255, 0.5);
        color: white;
    }

    /* История платежей */
    .payment-history-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 18px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        transition: background 0.2s ease;
    }

    .payment-history-row:last-child {
        border-bottom: none;
    }

    .payment-history-row:hover {
        background: rgba(255, 255, 255, 0.03);
    }

    .payment-badge-success {
        padding: 4px 12px;
        background: rgba(16, 185, 129, 0.15);
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        color: #10b981;
    }

    /* ===== СВЕТЛАЯ ТЕМА ДЛЯ КАБИНЕТА ===== */
    @media (prefers-color-scheme: light) {
        .cabinet-card {
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.2) 0%, rgba(100, 110, 255, 0.15) 100%),
                        rgba(255, 255, 255, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
        }

        .cabinet-card *, .cabinet-card-title, .profile-field-value,
        .history-row-title, .notification-title, .billing-info-value,
        .locked-section-title {
            color: #1e293b !important;
        }

        .cabinet-card::before {
            background: linear-gradient(90deg, transparent, rgba(79, 70, 229, 0.3), transparent);
        }

        .profile-field, .history-row, .notification-card {
            background: rgba(255, 255, 255, 0.5) !important;
            border-color: rgba(0, 0, 0, 0.06) !important;
        }

        .billing-status-card {
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.3) 0%, rgba(100, 110, 255, 0.2) 100%),
                        rgba(255, 255, 255, 0.5) !important;
            border-color: rgba(79, 70, 229, 0.2) !important;
        }

        .billing-info-item {
            background: rgba(255, 255, 255, 0.5) !important;
            border-color: rgba(0, 0, 0, 0.06) !important;
        }

        .locked-section {
            background: rgba(255, 255, 255, 0.4) !important;
            border-color: rgba(0, 0, 0, 0.1) !important;
        }

        .cabinet-header {
            border-bottom-color: rgba(0, 0, 0, 0.08);
        }

        .cabinet-header h2 {
            -webkit-text-fill-color: initial;
            background: none;
            color: #1e293b !important;
        }

        .cabinet-back-btn {
            background: rgba(255, 255, 255, 0.7) !important;
            border-color: rgba(0, 0, 0, 0.1) !important;
            color: #1e293b !important;
        }

        .profile-field-label, .history-row-meta, .notification-text,
        .notification-time, .billing-info-label, .locked-section-text {
            color: #64748b !important;
        }
    }

    /* ============================================================ */
    /* ========== АДАПТИВНЫЕ МЕДИА-ЗАПРОСЫ (MOBILE-FIRST) ========== */
    /* ============================================================ */

    /* === АДАПТИВНЫЙ .block-container ПО БРЕЙКПОИНТАМ === */
    @media (min-width: 768px) {
        .block-container {
            padding-top: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    }

    @media (min-width: 1440px) {
        .block-container {
            padding-left: 3rem;
            padding-right: 3rem;
        }
    }

    /* === MOBILE: ВЕРТИКАЛЬНЫЙ СТЕК КОЛОНОК НА ЭКРАНАХ < 768px === */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 8px !important;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }

    /* === MOBILE: ТАРИФНЫЕ КАРТОЧКИ === */
    @media (max-width: 768px) {
        .pricing-card-single, .pricing-card-pro {
            min-height: auto !important;
            padding: 24px 20px !important;
            border-radius: 24px !important;
            margin-bottom: 16px !important;
        }

        .pricing-card-single:hover, .pricing-card-pro:hover {
            transform: none !important;
        }

        /* Адаптивные шрифты внутри карточек */
        .pricing-card-single div[style*="font-size: 32px"],
        .pricing-card-pro div[style*="font-size: 32px"] {
            font-size: 26px !important;
        }

        .pricing-card-single div[style*="font-size: 20px"],
        .pricing-card-pro div[style*="font-size: 20px"] {
            font-size: 17px !important;
        }
    }

    @media (min-width: 769px) and (max-width: 1024px) {
        .pricing-card-single, .pricing-card-pro {
            padding: 30px !important;
            border-radius: 35px !important;
            min-height: 380px !important;
        }
    }

    /* === MOBILE: REPORT-CARD === */
    @media (max-width: 768px) {
        .report-card {
            padding: 20px 16px !important;
            border-radius: 20px !important;
            margin-top: 16px !important;
            margin-bottom: 20px !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
        }
    }

    /* === MOBILE: КНОПКИ (TOUCH-FRIENDLY: MIN 44-48px) === */
    @media (max-width: 768px) {
        .stButton > button, .login-btn-header button {
            padding: 16px 20px !important;
            font-size: 14px !important;
            min-height: 48px !important;
            border-radius: 16px !important;
        }

        .stDownloadButton > button {
            padding: 16px 20px !important;
            min-height: 48px !important;
            border-radius: 16px !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            transform: none !important;
        }
    }

    /* === MOBILE: ХЕДЕР ПРИЛОЖЕНИЯ === */
    @media (max-width: 480px) {
        .app-header-title {
            font-size: 22px !important;
        }

        .app-header-icon {
            font-size: 28px !important;
        }
    }

    @media (min-width: 481px) and (max-width: 768px) {
        .app-header-title {
            font-size: 26px !important;
        }
    }

    /* === MOBILE: ЛИЧНЫЙ КАБИНЕТ === */
    @media (max-width: 768px) {
        .cabinet-container {
            padding: 0 !important;
        }

        .cabinet-card {
            padding: 20px 16px !important;
            border-radius: 18px !important;
        }

        .cabinet-header h2 {
            font-size: 22px !important;
        }

        .profile-avatar-large {
            width: 80px !important;
            height: 80px !important;
            font-size: 32px !important;
        }

        .profile-field {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 10px !important;
            padding: 14px 16px !important;
        }

        .profile-field-action {
            width: 100% !important;
            text-align: center !important;
            padding: 12px !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* История */
        .history-row {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 12px !important;
            padding: 16px !important;
        }

        .history-row > div[style*="display: flex"] {
            width: 100% !important;
            flex-direction: column !important;
            gap: 10px !important;
        }

        .history-row-actions {
            width: 100% !important;
            justify-content: space-between !important;
        }

        .history-action-btn {
            padding: 10px 14px !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex: 1 !important;
        }

        /* Биллинг */
        .billing-info-grid {
            grid-template-columns: 1fr !important;
        }

        .billing-status-card {
            padding: 20px !important;
        }

        .billing-status-card div[style*="font-size: 28px"] {
            font-size: 22px !important;
        }

        /* Уведомления */
        .notification-card {
            flex-direction: column !important;
            gap: 10px !important;
        }

        .notification-time {
            align-self: flex-start !important;
        }
    }

    /* === MOBILE: МОДАЛЬНОЕ ОКНО АВТОРИЗАЦИИ === */
    @media (max-width: 768px) {
        [data-testid="stDialog"] {
            border-radius: 20px !important;
            margin: 10px !important;
        }

        [data-testid="stDialog"] [data-testid="stVerticalBlock"] {
            padding: 16px !important;
        }
    }

    /* === MOBILE: ЮРИДИЧЕСКИЙ ДИСКЛЕЙМЕР === */
    @media (max-width: 768px) {
        .disclaimer-glass {
            padding: 20px 16px 20px 22px !important;
            border-radius: 18px !important;
        }

        .disclaimer-glass h4 {
            font-size: 0.95rem !important;
        }

        .disclaimer-glass p {
            font-size: 0.85rem !important;
        }
    }

    /* === MOBILE: ШКАЛА РИСКА === */
    @media (max-width: 768px) {
        .risk-meter-container {
            padding: 6px !important;
            border-radius: 14px !important;
        }

        .risk-meter-container > div {
            font-size: 12px !important;
            height: 28px !important;
        }
    }

    /* === MOBILE: PILLS (ПИЛЮЛИ) === */
    @media (max-width: 768px) {
        [data-testid="stPill"] {
            min-height: 44px !important;
            padding: 8px 14px !important;
        }

        [data-testid="stPill"] div p {
            font-size: 0.8rem !important;
        }
    }

    /* === MOBILE: LOCKED SECTION === */
    @media (max-width: 768px) {
        .locked-section {
            padding: 40px 20px !important;
        }

        .locked-section-icon {
            font-size: 36px !important;
        }

        .locked-section-title {
            font-size: 16px !important;
        }

        .locked-section-text {
            font-size: 13px !important;
        }

        .locked-section-btn {
            width: 100% !important;
            justify-content: center !important;
            padding: 14px 20px !important;
        }
    }

    /* === TOUCH DEVICES: :active ВМЕСТО :hover === */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button:active,
        .login-btn-header button:active {
            transform: scale(0.97) !important;
            opacity: 0.9 !important;
        }

        .pricing-card-single:active, .pricing-card-pro:active {
            transform: scale(0.98) !important;
        }

        .profile-field-action:active {
            transform: scale(0.97) !important;
            opacity: 0.85 !important;
        }

        .history-action-btn:active {
            transform: scale(0.95) !important;
            opacity: 0.85 !important;
        }

        /* Убираем hover-эффекты на тач-устройствах */
        .stButton > button:hover,
        .pricing-card-single:hover,
        .pricing-card-pro:hover,
        .stDownloadButton > button:hover,
        .profile-field:hover,
        .history-row:hover,
        .cabinet-card:hover {
            transform: none !important;
        }
    }

    /* === TABLET/MEDIUM: ХЕДЕР — КНОПКИ ОДНОСТРОЧНЫЕ (769–1564px) === */
    @media (min-width: 769px) and (max-width: 1564px) {
        /* Общие исправления для кнопок хедера */
        .stButton > button, .login-btn-header button {
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            padding: 10px 14px !important;
            font-size: 11px !important;
            min-height: 40px !important;
            letter-spacing: 0.5px !important;
        }
    }

    /* === SAFE AREA INSETS (iPhone с «notch») === */
    @supports (padding: env(safe-area-inset-top)) {
        .block-container {
            padding-left: max(1rem, env(safe-area-inset-left)) !important;
            padding-right: max(1rem, env(safe-area-inset-right)) !important;
            padding-bottom: max(1rem, env(safe-area-inset-bottom)) !important;
        }
    }

    /* === 4K / ULTRA-WIDE ОПТИМИЗАЦИЯ === */
    @media (min-width: 2560px) {
        .block-container {
            max-width: 1800px !important;
            margin: 0 auto !important;
            padding-left: 4rem !important;
            padding-right: 4rem !important;
        }

        .pricing-card-single, .pricing-card-pro {
            padding: 50px !important;
            min-height: 500px !important;
        }

        .report-card {
            padding: 50px !important;
        }

        .cabinet-container {
            max-width: 1400px !important;
        }

        .disclaimer-glass {
            padding: 40px !important;
        }
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
