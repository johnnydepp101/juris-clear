"""
Модуль аутентификации JurisClear AI.
Функции для регистрации, входа и выхода пользователей через Supabase Auth.
"""

try:
    from gotrue.errors import AuthApiError
except ImportError:
    # Fallback: на некоторых платформах (Streamlit Cloud) gotrue может быть недоступен напрямую
    AuthApiError = Exception


def sign_up(supabase, email: str, password: str, display_name: str = ""):
    """
    Регистрация нового пользователя.
    Возвращает (data, error_message).
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": display_name
                }
            }
        })
        
        # Проверяем, что пользователь действительно создан
        if response.user:
            return response, None
        else:
            return None, "Не удалось создать аккаунт. Попробуйте позже."
            
    except AuthApiError as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already been registered" in error_msg.lower():
            return None, "Пользователь с таким email уже зарегистрирован."
        elif "password" in error_msg.lower() and ("short" in error_msg.lower() or "least" in error_msg.lower()):
            return None, "Пароль слишком короткий. Минимум 6 символов."
        elif "invalid" in error_msg.lower() and "email" in error_msg.lower():
            return None, "Некорректный email адрес."
        else:
            return None, f"Ошибка регистрации: {error_msg}"
    except Exception as e:
        return None, f"Непредвиденная ошибка: {str(e)}"


def sign_in(supabase, email: str, password: str):
    """
    Вход пользователя по email и паролю.
    Возвращает (data, error_message).
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        
        if response.user:
            return response, None
        else:
            return None, "Неверный email или пароль."
            
    except AuthApiError as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() and ("credentials" in error_msg.lower() or "login" in error_msg.lower()):
            return None, "Неверный email или пароль."
        elif "email not confirmed" in error_msg.lower():
            return None, "Email не подтверждён. Проверьте почту для подтверждения аккаунта."
        else:
            return None, f"Ошибка входа: {error_msg}"
    except Exception as e:
        return None, f"Непредвиденная ошибка: {str(e)}"


def sign_out(supabase):
    """
    Выход пользователя.
    Возвращает (success, error_message).
    """
    try:
        supabase.auth.sign_out()
        return True, None
    except Exception as e:
        return False, f"Ошибка при выходе: {str(e)}"


def get_user_profile(supabase, user_id: str):
    """
    Получение профиля пользователя из таблицы profiles.
    Возвращает dict с данными профиля или None.
    """
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception:
        return None


def update_display_name(supabase, user_id: str, new_name: str):
    """
    Обновление display_name пользователя в таблице profiles.
    Возвращает (success: bool, error_message: str | None).
    """
    try:
        supabase.table("profiles").update({
            "display_name": new_name
        }).eq("id", user_id).execute()
        return True, None
    except Exception as e:
        return False, f"Ошибка при обновлении имени: {str(e)}"
