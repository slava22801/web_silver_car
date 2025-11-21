from fastapi import APIRouter, HTTPException, status, Request
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import os
from database.db_init import db, collection_cars, collection
from Schemas.car import carEntity, carsEntity
from core.logger import log_user_action, log_system_event, log_error

cars_router = APIRouter(prefix="/cars")


class CarUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    mileage: Optional[int] = None
    engine: Optional[str] = None
    transmition_box: Optional[str] = None
    gear: Optional[str] = None
    rudder: Optional[str] = None
    carcase: Optional[str] = None
    color: Optional[str] = None


@cars_router.get("", status_code=status.HTTP_200_OK)
async def get_cars(request: Request):
    try:
        log_system_event("GET_ALL_CARS", "Request to get all cars")
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
        
        log_system_event("GET_ALL_CARS", f"Successfully retrieved {len(result)} cars")
        return result
    except Exception as e:
        log_error(e, "GET_ALL_CARS")
        raise


@cars_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_car_by_id(id: str, request: Request):
    try:
        log_system_event("GET_CAR_BY_ID", f"Request to get car with ID: {id}")
        object_id = ObjectId(id)
    except InvalidId:
        log_system_event("GET_CAR_BY_ID", f"Invalid car ID format: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid car ID format"
        )
    
    car = db.cars.find_one({"_id": object_id})
    
    if car is None:
        log_system_event("GET_CAR_BY_ID", f"Car not found with ID: {id}", "WARNING")
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
    
    log_system_event("GET_CAR_BY_ID", f"Successfully retrieved car: {car_data.get('name', 'Unknown')}")
    return car_data


@cars_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_car_by_id(id: str):
    try:
        log_user_action("DELETE_CAR", details=f"Attempting to delete car with ID: {id}")
        object_id = ObjectId(id)
    except InvalidId:
        log_system_event("DELETE_CAR", f"Invalid car ID format: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid car ID format"
        )
    
    car = db.cars.find_one({"_id": object_id})
    
    if car is None:
        log_system_event("DELETE_CAR", f"Car not found with ID: {id}", "WARNING")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    car_name = car.get("name", "Unknown")
    
    # Удаляем файл фото, если он существует
    if car.get("photo_path"):
        photo_path = car["photo_path"]
        # Преобразуем путь /uploads/filename.jpg в uploads/filename.jpg
        file_path = photo_path.lstrip('/')
        file_full_path = Path(file_path)
        
        # Проверяем существование файла и удаляем его
        if file_full_path.exists():
            try:
                os.remove(file_full_path)
                log_system_event("DELETE_CAR", f"Photo file deleted: {photo_path}")
            except Exception as e:
                log_error(e, f"DELETE_CAR - Error deleting photo file: {photo_path}")
    
    result = db.cars.delete_one({"_id": object_id})
    
    if result.deleted_count == 1:
        log_user_action("DELETE_CAR", details=f"Successfully deleted car: {car_name} (ID: {id})")
        return {"message": "Car deleted successfully", "id": id}
    else:
        log_system_event("DELETE_CAR", f"Failed to delete car with ID: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete car"
        )


@cars_router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_car_by_id(id: str, car_update: CarUpdate, request: Request):
    try:
        log_user_action("UPDATE_CAR", details=f"Attempting to update car with ID: {id}")
        object_id = ObjectId(id)
    except InvalidId:
        log_system_event("UPDATE_CAR", f"Invalid car ID format: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid car ID format"
        )
    
    car = db.cars.find_one({"_id": object_id})
    
    if car is None:
        log_system_event("UPDATE_CAR", f"Car not found with ID: {id}", "WARNING")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Создаем словарь с полями для обновления (исключаем None значения и photo_path)
    update_data = car_update.model_dump(exclude_unset=True, exclude_none=True)
    # Исключаем photo_path из обновления, чтобы путь к фото не изменялся
    update_data.pop("photo_path", None)
    
    if not update_data:
        log_system_event("UPDATE_CAR", f"No fields to update for car ID: {id}", "WARNING")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    log_system_event("UPDATE_CAR", f"Updating fields: {list(update_data.keys())} for car ID: {id}")
    
    result = db.cars.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 1:
        # Получаем обновленный документ
        updated_car = db.cars.find_one({"_id": object_id})
        car_data = carEntity(updated_car)
        # Если есть photo_path, добавляем полный URL
        if car_data.get("photo_path"):
            base_url = str(request.base_url).rstrip('/')
            car_data["photo_url"] = f"{base_url}{car_data['photo_path']}"
        else:
            car_data["photo_url"] = None
        
        log_user_action("UPDATE_CAR", details=f"Successfully updated car: {car_data.get('name', 'Unknown')} (ID: {id})")
        return car_data
    else:
        log_system_event("UPDATE_CAR", f"Failed to update car with ID: {id}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update car"
        )