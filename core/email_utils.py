import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.logger import log_system_event, log_error


# Настройки SMTP для Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT_SSL = 465  # Порт 465 использует SSL с самого начала (SMTP_SSL)
SMTP_PORT_STARTTLS = 587  # Порт 587 использует STARTTLS (SMTP + starttls())
SMTP_TIMEOUT = 30  # Таймаут в секундах для подключения и операций
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
        text = msg.as_string()
        
        # Пытаемся подключиться через порт 465 (SSL)
        # Если не получается, пробуем порт 587 (STARTTLS)
        server = None
        try:
            # Попытка 1: Порт 465 с SSL
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT_SSL, timeout=SMTP_TIMEOUT)
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, text)
            server.quit()
            log_system_event("SEND_EMAIL", f"Order confirmation email sent successfully to {to_email} (port 465)")
            return True
        except (socket.timeout, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, OSError) as e:
            # Если порт 465 не работает, пробуем порт 587
            if server:
                try:
                    server.quit()
                except:
                    pass
            try:
                log_system_event("SEND_EMAIL", f"Port 465 failed, trying port 587: {str(e)}")
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT_STARTTLS, timeout=SMTP_TIMEOUT)
                server.starttls()
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.sendmail(EMAIL_FROM, to_email, text)
                server.quit()
                log_system_event("SEND_EMAIL", f"Order confirmation email sent successfully to {to_email} (port 587)")
                return True
            except Exception as e2:
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                raise e2
        
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
    except (socket.timeout, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected) as e:
        error_msg = (
            f"SEND_EMAIL - Connection/timeout error for {to_email}. "
            "Возможные причины:\n"
            "1. Проблемы с сетевым подключением на сервере\n"
            "2. Блокировка порта 465 файрволом\n"
            "3. Таймаут подключения к SMTP серверу\n"
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
        text = msg.as_string()
        
        # Пытаемся подключиться через порт 465 (SSL)
        # Если не получается, пробуем порт 587 (STARTTLS)
        server = None
        try:
            # Попытка 1: Порт 465 с SSL
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT_SSL, timeout=SMTP_TIMEOUT)
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, text)
            server.quit()
            log_system_event("SEND_EMAIL", f"Password reset email sent successfully to {to_email} (port 465)")
            return True
        except (socket.timeout, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, OSError) as e:
            # Если порт 465 не работает, пробуем порт 587
            if server:
                try:
                    server.quit()
                except:
                    pass
            try:
                log_system_event("SEND_EMAIL", f"Port 465 failed, trying port 587: {str(e)}")
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT_STARTTLS, timeout=SMTP_TIMEOUT)
                server.starttls()
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.sendmail(EMAIL_FROM, to_email, text)
                server.quit()
                log_system_event("SEND_EMAIL", f"Password reset email sent successfully to {to_email} (port 587)")
                return True
            except Exception as e2:
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                raise e2
        
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
    except (socket.timeout, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected) as e:
        error_msg = (
            f"SEND_EMAIL - Connection/timeout error for {to_email}. "
            "Возможные причины:\n"
            "1. Проблемы с сетевым подключением на сервере\n"
            "2. Блокировка порта 465 файрволом\n"
            "3. Таймаут подключения к SMTP серверу\n"
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

