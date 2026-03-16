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
            --bg-color: #dae1f1;
            --card-bg: rgba(255, 255, 255, 0.8);
            --text-color: #1e293b;
            --secondary-text: #64748b;
            --border-color: rgba(0, 0, 0, 0.1);
            --card-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            --header-color: #0f172a;

            /* Градиентные цвета для светлой темы */
            --bg-grad-1: #e2c9d6;
            --bg-grad-2: #dbb3e7;
            --bg-grad-3: #cbddee;
            --bg-grad-4: #cadced;
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
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(157, 0, 255, 0.45) 0%, transparent 50%), 
            radial-gradient(at 0% 100%, var(--bg-grad-vibrant) 0%, transparent 55%), 
            radial-gradient(at 45% 45%, var(--bg-grad-deep) 0%, transparent 75%),
            radial-gradient(at 100% 0%, var(--bg-grad-dark) 0%, transparent 50%);
        background-attachment: fixed;
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
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 450px;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        padding: 35px; border-radius: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        text-align: center; color: white;
        box-shadow: var(--card-shadow), inset 0 0 20px rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .pricing-card-pro {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 450px;
        background: rgba(157, 0, 255, 0.05);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        padding: 35px; border-radius: 40px; 
        border: 1px solid rgba(157, 0, 255, 0.2); 
        text-align: center; color: white;
        box-shadow: 0 20px 40px rgba(157, 0, 255, 0.15), inset 0 0 20px rgba(255, 255, 255, 0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .pricing-card-single:hover, .pricing-card-pro:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* КАРТОЧКА ОТЧЕТА */
    .report-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--border-color);
        padding: 35px; border-radius: 35px; 
        margin-top: 25px; color: var(--text-color);
        box-shadow: var(--card-shadow);
        margin-bottom: 35px;
        position: relative;
        overflow: hidden;
    }
    
    .report-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
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
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        font-size: 14px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        padding: 12px 24px !important;
    }

    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    .stLinkButton > a {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
    }

    .stDownloadButton > button:hover {
        border: 1px solid var(--accent-blue) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* СТИЛИ ДЛЯ ТАБЛИЦ В ОТЧЕТЕ */
    .report-card table {
        margin-top: 25px !important;
        margin-bottom: 40px !important;
        border-collapse: collapse;
        width: 100%;
    }

    /* МАЛЕНЬКИЕ УЛУЧШЕНИЯ ТИПОГРАФИКИ */
    .secondary-text {
        color: var(--secondary-text);
        font-size: 0.9rem;
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
