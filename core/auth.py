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
    Обновление имени пользователя в таблице profiles и в user_metadata (auth).
    Возвращает (success: bool, error_message: str | None).
    """
    try:
        # Обновляем в таблице profiles
        supabase.table("profiles").update({
            "display_name": new_name
        }).eq("id", user_id).execute()
        
        # Обновляем в auth user_metadata
        supabase.auth.update_user({
            "data": {"display_name": new_name}
        })
        
        return True, None
    except Exception as e:
        return False, f"Ошибка обновления имени: {str(e)}"


def update_user_email(supabase, new_email: str):
    """
    Смена email пользователя через Supabase Auth.
    Поскольку email-подтверждение отключено, изменение вступает в силу сразу.
    Возвращает (success: bool, error_message: str | None).
    """
    try:
        supabase.auth.update_user({
            "email": new_email
        })
        return True, None
    except AuthApiError as e:
        error_msg = str(e)
        if "already" in error_msg.lower():
            return False, "Этот email уже используется другим аккаунтом."
        elif "invalid" in error_msg.lower():
            return False, "Некорректный email адрес."
        else:
            return False, f"Ошибка смены email: {error_msg}"
    except Exception as e:
        return False, f"Непредвиденная ошибка: {str(e)}"


def update_user_password(supabase, new_password: str):
    """
    Смена пароля пользователя через Supabase Auth.
    Возвращает (success: bool, error_message: str | None).
    """
    try:
        if len(new_password) < 6:
            return False, "Пароль должен содержать минимум 6 символов."
        
        supabase.auth.update_user({
            "password": new_password
        })
        return True, None
    except AuthApiError as e:
        error_msg = str(e)
        if "same" in error_msg.lower() or "identical" in error_msg.lower():
            return False, "Новый пароль совпадает с текущим."
        else:
            return False, f"Ошибка смены пароля: {error_msg}"
    except Exception as e:
        return False, f"Непредвиденная ошибка: {str(e)}"


def update_profile_fields(supabase, user_id: str, fields: dict):
    """
    Обновление дополнительных полей профиля (phone, company, position, language, timezone).
    fields — словарь с ключами-именами колонок и их новыми значениями.
    Возвращает (success: bool, error_message: str | None).
    """
    allowed_fields = {"phone", "company", "position", "language", "timezone"}
    filtered = {k: v for k, v in fields.items() if k in allowed_fields}
    
    if not filtered:
        return False, "Нет допустимых полей для обновления."
    
    try:
        supabase.table("profiles").update(filtered).eq("id", user_id).execute()
        return True, None
    except Exception as e:
        return False, f"Ошибка обновления профиля: {str(e)}"


def delete_user_account(project_url: str, service_key: str, user_id: str):
    """
    Удаление аккаунта пользователя через Edge Function delete-user.
    Возвращает (success: bool, error_message: str | None).
    """
    try:
        import requests
        delete_url = f"{project_url}/functions/v1/delete-user"
        resp = requests.post(
            delete_url,
            json={"user_id": user_id},
            headers={
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json"
            },
            timeout=15
        )
        if resp.status_code == 200:
            return True, None
        else:
            error_data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            return False, error_data.get("error", f"Ошибка сервера (код {resp.status_code})")
    except Exception as e:
        return False, f"Ошибка удаления аккаунта: {str(e)}"
