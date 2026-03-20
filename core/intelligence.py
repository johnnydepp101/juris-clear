import streamlit as st
import re

def analyze_long_text(client, full_text, contract_type, user_role, special_instructions, prompt_instruction):
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

def generate_analysis(client, full_text, contract_type, user_role, special_reqs):

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

def compare_documents(client, original_text, revised_text, contract_type, user_role):
    st.info("⏳ ИИ сравнивает версии документов и ищет юридически значимые изменения...")
    
    prompt = f"""
    Ты — профессиональный корпоративный юрист.
    Тебе предоставлены две версии одного договора (Тип: {contract_type}). Твоя роль — защитить интересы стороны: {user_role}.
    Тебе нужно найти и проанализировать все юридически значимые изменения между оригинальной версией и измененной.
    
    Оригинальная версия:
    ---
    {original_text[:15000]}
    ---
    
    Измененная версия:
    ---
    {revised_text[:15000]}
    ---
    
    СТРУКТУРА ОТВЕТА В MARKDOWN (ОБЯЗАТЕЛЬНО):
    ## 🔍 Обзор изменений
    [Краткий вывод о характере внесенных изменений, кто от них выигрывает в первую очередь]

    ## ⚖️ Анализ критических правок
    [Перечисли только те изменения, которые реально влияют на права, обязанности, ответственность, сроки и финансы.
    Для каждого изменения укажи:
    - 📄 Было: [суть как было]
    - 📝 Стало: [суть как стало]
    - ⚠️ Оценка риска для {user_role}: [Твой комментарий как юриста (используй 🔴, 🟠, 🟢)]]
    """
    
    progress_bar = st.progress(50)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    progress_bar.progress(100)
    progress_bar.empty()
    
    return response.choices[0].message.content

