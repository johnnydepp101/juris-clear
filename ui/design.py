import streamlit as st

def load_css():
    st.markdown("""
    <style>
    /* 1. ПЕРЕМЕННЫЕ ПО УМОЛЧАНИЮ (DARK THEME) - Цвета: 593bbe, 342a52, 5a79ea, d235e8, 76e5ff, 3f5fdf, 314dac */
    :root {
        --bg-gradient: linear-gradient(135deg, #342a52 0%, #593bbe 25%, #3f5fdf 50%, #5a79ea 75%, #314dac 100%);
        --card-bg: rgba(255, 255, 255, 0.07);
        --text-color: #f8fafc;
        --secondary-text: rgba(248, 250, 252, 0.7);
        --border-color: rgba(255, 255, 255, 0.15);
        --accent-blue: #76e5ff;
        --accent-purple: #d235e8;
        --glass-blur: blur(16px);
        --card-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        --header-color: #ffffff;
        --btn-bg: linear-gradient(135deg, #593bbe 0%, #d235e8 100%);
        --pill-bg: rgba(255, 255, 255, 0.1);
        --pill-selected: linear-gradient(135deg, #d235e8 0%, #593bbe 100%);
    }

    /* 2. СВЕТЛАЯ ТЕМА - Цвета: e9f0fe, e5cefa, e9d8d9, c7deeb, dbd2e0 */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-gradient: linear-gradient(135deg, #e9f0fe 0%, #e5cefa 25%, #dbd2e0 50%, #e9d8d9 75%, #c7deeb 100%);
            --card-bg: rgba(255, 255, 255, 0.3);
            --text-color: #1e293b;
            --secondary-text: rgba(30, 41, 59, 0.7);
            --border-color: rgba(0, 0, 0, 0.08);
            --card-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
            --header-color: #0f172a;
            --btn-bg: linear-gradient(135deg, #a78bfa 0%, #f472b6 100%);
            --pill-bg: rgba(0, 0, 0, 0.05);
            --pill-selected: linear-gradient(135deg, #f472b6 0%, #a78bfa 100%);
        }
    }

    /* СТРЕЙМЛИТ СТАНДАРТНЫЕ ЭЛЕМЕНТЫ */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    .block-container {
        padding-top: 3rem; 
        max-width: 1200px;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* ГЛОБАЛЬНЫЙ ФОН */
    [data-testid="stAppViewContainer"] {
        background: var(--bg-gradient) !important;
        background-attachment: fixed !important;
        color: var(--text-color);
        transition: all 0.4s ease;
    }

    /* УБИРАЕМ ЯКОРЯ */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, 
    .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a { display: none !important; }
    [data-testid="stMarkdownHeader"] a { display: none !important; }

    /* ХЕДЕР И ВЫРАВНИВАНИЕ */
    [data-testid="stHorizontalBlock"] { align-items: center !important; }

    /* КАРТОЧКИ (GLASSMORPHISM) */
    .pricing-card-single, .pricing-card-pro, .report-card {
        background: var(--card-bg) !important;
        backdrop-filter: var(--glass-blur) !important;
        -webkit-backdrop-filter: var(--glass-blur) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 20px !important;
        box-shadow: var(--card-shadow) !important;
        padding: 24px !important;
        transition: transform 0.3s ease, border-color 0.3s ease !important;
    }
    
    .pricing-card-single:hover, .pricing-card-pro:hover, .report-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.3) !important;
    }

    /* СПЕЦИФИКА КАРТОЧКИ ОТЧЕТА */
    .report-card {
        border-left: 6px solid var(--accent-purple) !important;
        margin-top: 25px;
        margin-bottom: 35px;
    }
    
    /* ШКАЛА РИСКА */
    .risk-meter-container {
        background: rgba(0, 0, 0, 0.15); 
        border-radius: 20px; 
        padding: 6px;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.2); 
        border: 1px solid var(--border-color); 
        margin: 20px 0;
    }
    
    /* КНОПКИ */
    .stButton > button {
        background: var(--btn-bg) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 14px !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        padding: 14px 28px !important;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }

    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(210, 53, 232, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    
    /* ST.PILLS - ПЕРЕНАСТРОЙКА ПОД GLASSMORPHISM */
    [data-testid="stPill"] {
        background: var(--pill-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 20px !important;
        color: var(--text-color) !important;
        backdrop-filter: var(--glass-blur) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stPill"][aria-pressed="true"] {
        background: var(--pill-selected) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 4px 12px rgba(210, 53, 232, 0.2) !important;
    }

    /* ТИПОГРАФИКА */
    h1, h2, h3, h4 {
        color: var(--header-color) !important;
        letter-spacing: -0.5px !important;
    }

    .secondary-text {
        color: var(--secondary-text);
        font-size: 0.95rem;
    }

    /* ЮРИДИЧЕСКИЙ ДИСКЛЕЙМЕР */
    .disclaimer-glass {
        background: rgba(239, 68, 68, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 2px solid rgba(239, 68, 68, 0.4) !important;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 25px;
        color: var(--text-color);
        box-shadow: 0 8px 32px 0 rgba(239, 68, 68, 0.1) !important;
    }
    
    .disclaimer-glass h4 {
        color: #ef4444 !important;
        margin-top: 0;
    }

    /* АНИМАЦИИ */
    @keyframes glass-shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .stDownloadButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-color) !important;
        border-radius: 12px !important;
    }

    .stDownloadButton > button:hover {
        border-color: var(--accent-blue) !important;
        background: rgba(255, 255, 255, 0.1) !important;
    }
    </style>
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
