from fastapi import APIRouter, HTTPException, status
from pymongo import MongoClient
from database.db_init import db, collection_cars, collection
from Schemas.car import carEntity, carsEntity

cars_router = APIRouter(prefix="/cars")


@cars_router.get("")
async def get_users():
    res = (carsEntity(db.cars.find()))
    return res