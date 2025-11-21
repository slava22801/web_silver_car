from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from database.db_init import db
from auth import utils as auth_utils
from Schemas.schemas import TokenInfo, UserSchema, AutoInfo
import uuid
from pathlib import Path
from core.logger import log_user_action, log_system_event, log_error


admin_router = APIRouter(prefix="/admin")

# Создаем папку uploads если её нет
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@admin_router.post("/login", status_code=status.HTTP_200_OK)
async def auth_admin_issue_jwt(
    user: UserSchema = Depends(auth_utils.validate_auth_user),
):
    try:
        log_user_action("ADMIN_LOGIN", user_id=str(user["_id"]), username=user["username"], 
                       details=f"Admin login attempt: {user['email']}")
        
        jwt_payload = {
            "sub": user["username"],
            "username": user["username"],
            "email": user["email"],
        }
        token = auth_utils.encode_jwt(jwt_payload)
        
        log_user_action("ADMIN_LOGIN", user_id=str(user["_id"]), username=user["username"], 
                       details=f"Successfully logged in as admin: {user['email']}")
        
        return TokenInfo(
            access_token=token,
            token_type="Bearer"
        )
    except Exception as e:
        log_error(e, f"ADMIN_LOGIN - {user.get('email', 'Unknown')}")
        raise
    
    
@admin_router.post("/add_car", status_code=status.HTTP_201_CREATED)
async def add_car(
    name: str = Form(...),
    price: int = Form(...),
    mileage: int = Form(...),
    engine: str = Form(...),
    transmition_box: str = Form(...),
    gear: str = Form(...),
    rudder: str = Form(...),
    carcase: str = Form(...),
    color: str = Form(...),
    photo: UploadFile = File(...)
):
    try:
        log_user_action("ADMIN_ADD_CAR", details=f"Attempting to add new car: {name}")
        
        # Проверяем тип файла
        if not photo.content_type or not photo.content_type.startswith('image/'):
            log_system_event("ADMIN_ADD_CAR", f"Invalid file type for car: {name}", "ERROR")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")
        
        # Генерируем уникальное имя файла
        file_extension = Path(photo.filename).suffix if photo.filename else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Сохраняем файл
        try:
            with open(file_path, "wb") as buffer:
                content = await photo.read()
                buffer.write(content)
            log_system_event("ADMIN_ADD_CAR", f"Photo file saved: {unique_filename}")
        except Exception as e:
            log_error(e, f"ADMIN_ADD_CAR - Error saving photo for car: {name}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error saving file: {str(e)}")
        
        # Сохраняем путь к файлу в БД (относительный путь для статики)
        photo_path = f"/uploads/{unique_filename}"
        
        result = db.cars.insert_one(
            {
                "name": name,
                "price": price,
                "mileage": mileage,
                "engine": engine,
                "transmition_box": transmition_box,
                "gear": gear,
                "rudder": rudder,
                "carcase": carcase,
                "color": color,
                "photo_path": photo_path
             } 
        )
        
        log_user_action("ADMIN_ADD_CAR", details=f"Successfully added car: {name} (ID: {result.inserted_id}, Price: {price})")
        return {"ok": True, "message": "Car added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"ADMIN_ADD_CAR - Car: {name}")
        raise
    
# @admin_router.get("/get_all_cars")
# async def get_cars():
#     try:
#         cars = db.cars.find().to_list(length=100)
        

        
#         return cars
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    