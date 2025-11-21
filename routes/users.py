from fastapi import APIRouter, Depends, status, HTTPException
from bson import ObjectId
from database.db_init import db
from auth import utils as auth_utils
from Schemas.schemas import TokenInfo, UserSchema, ChangePasswordSchema, ForgotPasswordSchema, ResetPasswordSchema
from Schemas.user import usersEntity
from core.logger import log_user_action, log_system_event, log_error
from core.email_utils import send_password_reset_email
from datetime import timedelta


users_router = APIRouter(prefix="/user")

@users_router.get("", status_code=status.HTTP_200_OK)
async def get_users():
    try:
        log_system_event("GET_ALL_USERS", "Request to get all users")
        users = usersEntity(db.users.find())
        log_system_event("GET_ALL_USERS", f"Successfully retrieved {len(users)} users")
        return users
    except Exception as e:
        log_error(e, "GET_ALL_USERS")
        raise

@users_router.post("/add_user", status_code=status.HTTP_201_CREATED)
async def add_user(user:UserSchema):
    try:
        user_data = user.model_dump()
        log_user_action("CREATE_USER", username=user_data["username"], details=f"Creating new user: {user_data['email']}")
        
        # Хешируем пароль перед сохранением
        hashed_password = auth_utils.hash_password(user_data["password"])
        
        result = db.users.insert_one(
            {
                "username": user_data["username"],
                "password": hashed_password,
                "email": user_data["email"],
                "role": user_data["role"]
             }
                            )
        
        log_user_action("CREATE_USER", user_id=str(result.inserted_id), username=user_data["username"], 
                        details=f"Successfully created user: {user_data['email']} with role: {user_data['role']}")
        
        return {"message": "Пользователь создан успешно", "id": str(result.inserted_id), "email": user_data["email"]}
    except Exception as e:
        log_error(e, f"CREATE_USER - {user_data.get('email', 'Unknown')}")
        raise
    
@users_router.post("/login", status_code=status.HTTP_200_OK)
async def auth_user_issue_jwt(
    user: UserSchema = Depends(auth_utils.validate_auth_user),
):
    try:
        log_user_action("USER_LOGIN", user_id=str(user["_id"]), username=user["username"], 
                       details=f"User login attempt: {user['email']}")
        
        jwt_payload = {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        }
        token = auth_utils.encode_jwt(jwt_payload)
        
        log_user_action("USER_LOGIN", user_id=str(user["_id"]), username=user["username"], 
                       details=f"Успешно авторизован: {user['email']}")
        
        return TokenInfo(
            access_token=token,
            token_type="Bearer"
        )
    except Exception as e:
        log_error(e, f"USER_LOGIN - {user.get('email', 'Unknown')}")
        raise


@users_router.put("/change_password", status_code=status.HTTP_200_OK)
async def change_password(password_data: ChangePasswordSchema):
    try:
        log_user_action("CHANGE_PASSWORD", details=f"Password change attempt for email: {password_data.email}")
        
        # Находим пользователя по email
        user = db.users.find_one({"email": password_data.email})
        
        if not user:
            log_system_event("CHANGE_PASSWORD", f"User not found with email: {password_data.email}", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Проверяем старый пароль
        stored_password = user.get('password', '')
        if not auth_utils.validate_password(password_data.old_password, stored_password):
            log_system_event("CHANGE_PASSWORD", f"Invalid old password for email: {password_data.email}", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid old password"
            )
        
        # Проверяем, что новый пароль отличается от старого
        if auth_utils.validate_password(password_data.new_password, stored_password):
            log_system_event("CHANGE_PASSWORD", f"New password is the same as old password for email: {password_data.email}", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from old password"
            )
        
        # Хешируем новый пароль
        hashed_new_password = auth_utils.hash_password(password_data.new_password)
        
        # Обновляем пароль в базе данных
        result = db.users.update_one(
            {"email": password_data.email},
            {"$set": {"password": hashed_new_password}}
        )
        
        if result.modified_count == 1:
            log_user_action("CHANGE_PASSWORD", user_id=str(user["_id"]), username=user.get("username"),
                           details=f"Successfully changed password for email: {password_data.email}")
            return {"message": "Пароль успешно изменен", "email": password_data.email}
        else:
            log_system_event("CHANGE_PASSWORD", f"Failed to update password for email: {password_data.email}", "ERROR")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"CHANGE_PASSWORD - Email: {password_data.email}")
        raise


@users_router.post("/forgot_password", status_code=status.HTTP_200_OK)
async def forgot_password(forgot_data: ForgotPasswordSchema):
    """
    Запрос на сброс пароля. Отправляет email с токеном для сброса пароля.
    """
    try:
        log_user_action("FORGOT_PASSWORD", details=f"Password reset request for email: {forgot_data.email}")
        
        # Находим пользователя по email
        user = db.users.find_one({"email": forgot_data.email})
        
        # Для безопасности не сообщаем, существует ли пользователь
        if not user:
            log_system_event("FORGOT_PASSWORD", f"Password reset requested for non-existent email: {forgot_data.email}", "WARNING")
            # Возвращаем успешный ответ даже если пользователь не найден (для безопасности)
            return {"message": "Если пользователь с таким email существует, письмо с инструкциями отправлено"}
        
        # Генерируем JWT токен для сброса пароля (действителен 1 час)
        reset_payload = {
            "email": forgot_data.email,
            "user_id": str(user["_id"]),
            "type": "password_reset"
        }
        
        # Используем короткое время жизни токена (1 час)
        reset_token = auth_utils.encode_jwt(
            reset_payload,
            expire_timedelta=timedelta(hours=1)
        )
        
        # Отправляем email с токеном
        email_sent = send_password_reset_email(
            to_email=forgot_data.email,
            reset_token=reset_token,
            username=user.get("username")
        )
        
        if email_sent:
            log_user_action("FORGOT_PASSWORD", user_id=str(user["_id"]), username=user.get("username"),
                           details=f"Password reset email sent successfully to {forgot_data.email}")
            return {"message": "Письмо с инструкциями по сбросу пароля отправлено на ваш email"}
        else:
            log_system_event("FORGOT_PASSWORD", f"Failed to send password reset email to {forgot_data.email}", "ERROR")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"FORGOT_PASSWORD - Email: {forgot_data.email}")
        raise


@users_router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(reset_data: ResetPasswordSchema):
    """
    Сброс пароля с использованием токена из email.
    """
    try:
        log_user_action("RESET_PASSWORD", details="Password reset attempt with token")
        
        # Декодируем токен
        try:
            decoded_token = auth_utils.decode_jwt(reset_data.token)
        except Exception as e:
            log_system_event("RESET_PASSWORD", f"Invalid or expired reset token: {str(e)}", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Проверяем тип токена
        if decoded_token.get("type") != "password_reset":
            log_system_event("RESET_PASSWORD", "Invalid token type", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        
        email = decoded_token.get("email")
        user_id = decoded_token.get("user_id")
        
        if not email or not user_id:
            log_system_event("RESET_PASSWORD", "Token missing required fields", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        
        # Находим пользователя
        try:
            user_object_id = ObjectId(user_id)
        except:
            log_system_event("RESET_PASSWORD", f"Invalid user_id format: {user_id}", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        
        user = db.users.find_one({"email": email, "_id": user_object_id})
        
        if not user:
            log_system_event("RESET_PASSWORD", f"User not found for email: {email}", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Хешируем новый пароль
        hashed_new_password = auth_utils.hash_password(reset_data.new_password)
        
        # Обновляем пароль в базе данных
        result = db.users.update_one(
            {"email": email},
            {"$set": {"password": hashed_new_password}}
        )
        
        if result.modified_count == 1:
            log_user_action("RESET_PASSWORD", user_id=str(user["_id"]), username=user.get("username"),
                           details=f"Successfully reset password for email: {email}")
            return {"message": "Пароль успешно сброшен", "email": email}
        else:
            log_system_event("RESET_PASSWORD", f"Failed to update password for email: {email}", "ERROR")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "RESET_PASSWORD")
        raise