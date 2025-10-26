from datetime import timedelta, datetime
from database.db_init import db
from fastapi import Form, HTTPException, status
from core.config import settings
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
    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
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
    salt = bcrypt.gensalt(rounds=12)
    pwd_bytes: bytes = password.encode('utf-8')
    return bcrypt.hashpw(pwd_bytes, salt)


# def validate_password(
#     password: str,
#     hashed_password: bytes
# ) -> bool:
#     return bcrypt.checkpw(
#         password=password.encode(),
#         hashed_password=hashed_password
#     )

# def validate_password(password: str, hashed_password) -> bool:
#     """
#     Универсальная проверка пароля, работает с:
#     - строками
#     - bytes
#     - None значениями
#     """
#     try:
#         # Проверяем наличие данных
#         if not password or not hashed_password:
#             return False
        
#         # Конвертируем plain_password в bytes
#         if isinstance(password, str):
#             password_bytes = password.encode('utf-8')
#         elif isinstance(password, bytes):
#             password_bytes = password
#         else:
#             return False
        
#         # Конвертируем hashed_password в bytes
#         if isinstance(hashed_password, str):
#             hashed_bytes = hashed_password.encode('utf-8')
#         elif isinstance(hashed_password, bytes):
#             hashed_bytes = hashed_password
#         else:
#             return False
        
#         # Проверяем пароль
#         return bcrypt.checkpw(password_bytes, hashed_bytes)
        
#     except Exception as e:
#         print(f"Password verification error: {e}")
#         return False



def validate_auth_user(
    username: str = Form(),
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
    if (user := db.users.find_one({"username": username})):
        result = db.users.find_one({"username": username})
        if password == {result.get('password')}:
            raise unauthed_exc_psw

    # if not validate_password(
    #     password=password,
    #     hashed_password=user["password"],
    # ):
    #     raise unauthed_exc
    # if password == {result.get('password')}:
    #     raise unauthed_exc_psw

    
    # if not user.active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="user inactive"
    #     )
    return user