import streamlit as st
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from io import BytesIO

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
