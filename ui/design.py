import streamlit as st

def load_css(theme="Auto"):
    # 1. ПЕРЕМЕННЫЕ ТЕМНОЙ ТЕМЫ (ПО УМОЛЧАНИЮ)
    DARK_VARS = """
        --bg-color: #01010a;
        --card-bg: rgba(255, 255, 255, 0.03);
        --text-color: #f0f6fc;
        --secondary-text: #8b949e;
        --border-color: rgba(255, 255, 255, 0.12);
        --accent-blue: #3b82f6;
        --accent-green: #10b981;
        --glass-blur: blur(25px);
        --card-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        --header-color: #ffffff;
        --bg-grad-vibrant: #190e20;
        --bg-grad-deep: #05053a;
        --bg-grad-dark: #01010a;
    """

    DARK_BG = """
        [data-testid="stAppViewContainer"] {
            background-color: var(--bg-color) !important;
            background-image: 
                radial-gradient(at 85% 15%, var(--bg-grad-vibrant) 0%, transparent 60%),
                radial-gradient(at 15% 85%, var(--bg-grad-deep) 0%, transparent 60%),
                radial-gradient(at 50% 50%, var(--bg-grad-dark) 0%, transparent 100%) !important;
            background-attachment: fixed !important;
            background-size: cover !important;
            color: var(--text-color);
            transition: all 0.4s ease;
        }
    """
    
    # 2. ПЕРЕМЕННЫЕ И ОВЕРРАЙДЫ СВЕТЛОЙ ТЕМЫ
    LIGHT_VARS = """
        --bg-color: #ffffff;
        --card-bg: rgba(255, 255, 255, 0.7);
        --text-color: #01010a;
        --secondary-text: #475569;
        --border-color: rgba(0, 0, 0, 0.1);
        --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        --header-color: #01010a;
        --bg-grad-vibrant: rgba(255, 120, 240, 0.45);
        --bg-grad-deep: rgba(100, 110, 255, 0.45);
        --bg-grad-dark: #ffffff;
    """

    LIGHT_BG = """
        [data-testid="stAppViewContainer"] {
            background-image: 
                radial-gradient(at 85% 15%, rgba(255, 120, 240, 0.45) 0%, transparent 50%),
                radial-gradient(at 15% 85%, rgba(100, 110, 255, 0.45) 0%, transparent 50%),
                linear-gradient(to bottom, #ffffff, #f0f2f6) !important;
        }
    """

    LIGHT_OVERRIDES = """
        .pricing-card-single, .pricing-card-pro, .report-card {
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.35) 0%, rgba(100, 110, 255, 0.25) 100%), 
                        rgba(255, 255, 255, 0.5) !important;
            backdrop-filter: blur(30px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(30px) saturate(160%) !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            box-shadow: 0 15px 45px rgba(0, 0, 0, 0.05) !important;
            color: #1e293b !important;
        }
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
        .stTabs [data-baseweb="tab"] {
            color: #475569 !important;
            font-weight: 600 !important;
            background: transparent !important;
            border: none !important;
        }
        .stTabs [aria-selected="true"], .stTabs [aria-selected="true"] * {
            color: #01010a !important;
            font-weight: 900 !important;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(79, 70, 229, 0.1) !important;
            border-radius: 12px 12px 0 0 !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #4f46e5 !important;
            height: 3px !important;
        }
        [data-testid="stPill"][aria-selected="true"] {
            background: rgba(79, 70, 229, 0.15) !important;
            border: 2px solid #4f46e5 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1) !important;
        }
        [data-testid="stPill"][aria-selected="true"] *, [data-testid="stPill"][aria-selected="true"] p {
            color: #01010a !important;
            font-weight: 800 !important;
        }
        .stButton > button {
            color: #ffffff !important;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        }
        [data-testid="stDownloadButton"] button, [data-testid="stDownloadButton"] button *,
        .stDownloadButton > button, .stDownloadButton > button * {
            color: #01010a !important;
            font-weight: 900 !important;
        }
        .stDownloadButton > button {
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.45) 0%, rgba(100, 110, 255, 0.35) 100%), 
                        rgba(255, 255, 255, 0.6) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(20px) !important;
        }
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, rgba(255, 178, 239, 0.55) 0%, rgba(100, 110, 255, 0.45) 100%) !important;
        }
        .stTextInput input, .stTextArea textarea {
            background-color: #ffffff !important;
            color: #01010a !important;
            border: 1.5px solid rgba(0, 0, 0, 0.1) !important;
        }
    """

    # 3. ОБЩИЕ СТИЛИ (COMMON)
    COMMON_STYLES = """
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        [data-testid="stHeader"] {display: none;}
        
        .block-container {
            padding-top: 2rem; 
            max-width: 100%;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, 
        .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a { display: none !important; }
        [data-testid="stMarkdownHeader"] a { display: none !important; }

        [data-testid="stHorizontalBlock"] { align-items: center !important; }

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
        
        .pricing-card-single:hover, .pricing-card-pro:hover {
            transform: translateY(-12px) scale(1.02);
            border-color: rgba(157, 0, 255, 1);
            background: rgba(157, 0, 255, 0.05);
        }
        
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
        
        .stButton > button, .login-btn-header button, .theme-toggle button {
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

        .stButton > button:hover, .login-btn-header button:hover, .theme-toggle button:hover {
            box-shadow: 0 0 25px rgba(157, 0, 255, 0.5) !important;
            border: 1px solid rgba(157, 0, 255, 1) !important;
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

        .disclaimer-glass {
            background: rgba(255, 75, 75, 0.08);
            backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 75, 75, 0.4);
            padding: 30px; border-radius: 30px; 
            margin-bottom: 30px;
        }

        [data-testid="stPill"] {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 15px !important;
            backdrop-filter: blur(5px) !important;
        }

        /* СПЕЦИАЛЬНЫЙ СТИЛЬ ДЛЯ ПЕРЕКЛЮЧАТЕЛЯ ТЕМ */
        .theme-toggle button {
            padding: 14px 18px !important;
            min-width: 60px !important;
            font-size: 18px !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
    """

    # Сборка финального CSS
    if theme == "Dark":
        css = f":root {{ {DARK_VARS} }} {DARK_BG} {COMMON_STYLES}"
    elif theme == "Light":
        css = f":root {{ {LIGHT_VARS} }} {LIGHT_BG} {COMMON_STYLES} {LIGHT_OVERRIDES}"
    else: # Auto (Системный)
        css = f":root {{ {DARK_VARS} }} {DARK_BG} {COMMON_STYLES} " \
              f"@media (prefers-color-scheme: light) {{ :root {{ {LIGHT_VARS} }} {LIGHT_BG} {LIGHT_OVERRIDES} }}"

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

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
