from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["silver_car"]
collection = db["users"]
        

