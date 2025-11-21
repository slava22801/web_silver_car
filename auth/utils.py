from datetime import timedelta, datetime
from database.db_init import db
from fastapi import Form, HTTPException, status
from core.config import settings
from core.logger import log_system_event, log_error
import bcrypt

import jwt

def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded

def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(
    password: str
) -> str:
    """
    Хеширует пароль с использованием bcrypt
    Возвращает строку в формате, пригодном для хранения в БД
    """
    salt = bcrypt.gensalt(rounds=12)
    pwd_bytes: bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    # Декодируем bytes в строку для хранения в MongoDB
    return hashed.decode('utf-8')


def validate_password(password: str, hashed_password: str) -> bool:
    """
    Проверяет пароль против хешированного пароля
    Работает с строками (хеш из БД) и bytes
    """
    try:
        # Проверяем наличие данных
        if not password or not hashed_password:
            return False
        
        # Конвертируем plain_password в bytes
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')
        elif isinstance(password, bytes):
            password_bytes = password
        else:
            return False
        
        # Конвертируем hashed_password в bytes
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        elif isinstance(hashed_password, bytes):
            hashed_bytes = hashed_password
        else:
            return False
        
        # Проверяем пароль
        return bcrypt.checkpw(password_bytes, hashed_bytes)
        
    except Exception as e:
        log_error(e, "VALIDATE_PASSWORD")
        return False


def validate_auth_user(
    email: str = Form(),
    password: str = Form()
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )
    unauthed_exc_psw = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password"
    )
    
    try:
        user = db.users.find_one({"email": email})
        
        if not user:
            log_system_event("AUTH_VALIDATION", f"Login attempt with non-existent email: {email}", "WARNING")
            raise unauthed_exc
        
        # Проверяем пароль с использованием bcrypt
        stored_password = user.get('password', '')
        if not validate_password(password, stored_password):
            log_system_event("AUTH_VALIDATION", f"Invalid password attempt for email: {email}", "WARNING")
            raise unauthed_exc_psw

        
        # if not user.active:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="user inactive"
        #     )
        return user
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"AUTH_VALIDATION - Email: {email}")
        raise