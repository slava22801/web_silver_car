import os
from pymongo import MongoClient


# Получаем URL подключения к MongoDB из переменной окружения или используем значение по умолчанию
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "silver_car")

client = MongoClient(MONGODB_URL)
db = client[MONGODB_DB_NAME]
collection = db["users"]
collection_cars = db["cars"]
