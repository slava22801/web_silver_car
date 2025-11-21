import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.logger import log_system_event, log_error


# Настройки SMTP для Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = "carsilver622@gmail.com"
# ВАЖНО: Используйте пароль приложения (App Password), а не обычный пароль!
# Как получить пароль приложения:
# 1. Войдите в аккаунт Google: https://myaccount.google.com/
# 2. Перейдите в "Безопасность" -> "Двухэтапная аутентификация" (должна быть включена)
# 3. Внизу страницы найдите "Пароли приложений"
# 4. Создайте новый пароль приложения для "Почта" и "Другое устройство"
# 5. Скопируйте 16-значный пароль и вставьте его сюда
EMAIL_PASSWORD = "psvguaeptmszejlh"  # Пароль приложения (без пробелов)


def send_order_confirmation_email(to_email: str, order_data: dict) -> bool:
    """
    Отправляет письмо с подтверждением заказа
    
    Args:
        to_email: Email получателя
        order_data: Данные заказа (name, auto_name, number, comment, status)
    
    Returns:
        bool: True если письмо отправлено успешно, False в противном случае
    """
    try:
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = "Подтверждение заказа - Silver Car"
        
        # Формируем тело письма
        body = f"""
Здравствуйте, {order_data.get('name', 'Клиент')}!

Ваш заказ успешно создан.

Детали заказа:
- Автомобиль: {order_data.get('auto_name', 'Не указан')}
- Номер телефона: {order_data.get('number', 'Не указан')}
- Комментарий: {order_data.get('comment', 'Нет комментария')}
- Статус: {order_data.get('status', 'В ожидании')}

Мы свяжемся с вами в ближайшее время.

С уважением,
Команда Silver Car
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Подключаемся к SMTP серверу и отправляем письмо
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Включаем TLS шифрование
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, to_email, text)
        server.quit()
        
        log_system_event("SEND_EMAIL", f"Order confirmation email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = (
            f"SEND_EMAIL - Authentication error for {to_email}. "
            "Возможные причины:\n"
            "1. Неверный пароль - используйте пароль приложения (App Password), а не обычный пароль\n"
            "2. Двухэтапная аутентификация не включена\n"
            "3. Пароль приложения не создан\n"
            f"Ошибка: {str(e)}"
        )
        log_error(e, error_msg)
        return False
    except smtplib.SMTPException as e:
        log_error(e, f"SEND_EMAIL - SMTP error for {to_email}")
        return False
    except Exception as e:
        log_error(e, f"SEND_EMAIL - Error sending email to {to_email}")
        return False


def send_password_reset_email(to_email: str, reset_token: str, username: str = None) -> bool:
    """
    Отправляет письмо со ссылкой для сброса пароля
    
    Args:
        to_email: Email получателя
        reset_token: Токен для сброса пароля
        username: Имя пользователя (опционально)
    
    Returns:
        bool: True если письмо отправлено успешно, False в противном случае
    """
    try:
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = "Сброс пароля - Silver Car"
        
        # Формируем тело письма
        name = username if username else "Клиент"
        body = f"""
Здравствуйте, {name}!

Вы запросили сброс пароля для вашего аккаунта в Silver Car.

Для сброса пароля используйте следующий токен:
{reset_token}

Токен действителен в течение 1 часа.

Если вы не запрашивали сброс пароля, проигнорируйте это письмо.

С уважением,
Команда Silver Car
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Подключаемся к SMTP серверу и отправляем письмо
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Включаем TLS шифрование
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, to_email, text)
        server.quit()
        
        log_system_event("SEND_EMAIL", f"Password reset email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = (
            f"SEND_EMAIL - Authentication error for {to_email}. "
            "Возможные причины:\n"
            "1. Неверный пароль - используйте пароль приложения (App Password), а не обычный пароль\n"
            "2. Двухэтапная аутентификация не включена\n"
            "3. Пароль приложения не создан\n"
            f"Ошибка: {str(e)}"
        )
        log_error(e, error_msg)
        return False
    except smtplib.SMTPException as e:
        log_error(e, f"SEND_EMAIL - SMTP error for {to_email}")
        return False
    except Exception as e:
        log_error(e, f"SEND_EMAIL - Error sending email to {to_email}")
        return False

