from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from database.db_init import db
from auth import utils as auth_utils
from Schemas.schemas import TokenInfo, UserSchema, AutoInfo
import uuid
from pathlib import Path


admin_router = APIRouter(prefix="/admin")

# Создаем папку uploads если её нет
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@admin_router.post("/login")
async def auth_admin_issue_jwt(
    user: UserSchema = Depends(auth_utils.validate_auth_user),
):
    jwt_payload = {
        "sub": user["username"],
        "username": user["username"],
        "email": user["email"],
    }
    token = auth_utils.encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer"
    )
    
    
@admin_router.post("/add_car")
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
    # Проверяем тип файла
    if not photo.content_type or not photo.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Генерируем уникальное имя файла
    file_extension = Path(photo.filename).suffix if photo.filename else '.jpg'
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Сохраняем файл
    try:
        with open(file_path, "wb") as buffer:
            content = await photo.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Сохраняем путь к файлу в БД (относительный путь для статики)
    photo_path = f"/uploads/{unique_filename}"
    
    db.cars.insert_one(
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
    return {"ok": True, "message": "Car added successfully"}
    
# @admin_router.get("/get_all_cars")
# async def get_cars():
#     try:
#         cars = db.cars.find().to_list(length=100)
        

        
#         return cars
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    