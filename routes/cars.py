from fastapi import APIRouter, HTTPException, status, Request
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from database.db_init import db, collection_cars, collection
from Schemas.car import carEntity, carsEntity

cars_router = APIRouter(prefix="/cars")


@cars_router.get("")
async def get_cars(request: Request):
    cars = list(db.cars.find())
    result = []
    
    for car in cars:
        car_data = carEntity(car)
        # Если есть photo_path, добавляем полный URL
        if car_data.get("photo_path"):
            base_url = str(request.base_url).rstrip('/')
            car_data["photo_url"] = f"{base_url}{car_data['photo_path']}"
        else:
            car_data["photo_url"] = None
        
        result.append(car_data)
    
    return result


@cars_router.get("/{id}")
async def get_car_by_id(id: str, request: Request):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid car ID format"
        )
    
    car = db.cars.find_one({"_id": object_id})
    
    if car is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    car_data = carEntity(car)
    # Если есть photo_path, добавляем полный URL
    if car_data.get("photo_path"):
        base_url = str(request.base_url).rstrip('/')
        car_data["photo_url"] = f"{base_url}{car_data['photo_path']}"
    else:
        car_data["photo_url"] = None
    
    return car_data