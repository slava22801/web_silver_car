from fastapi import APIRouter
from database.db_init import db


users_router = APIRouter(prefix="/user")

@users_router.get("/")
async def get_users():
    return {"users"}

@users_router.post("/add_user")
async def add_user():
    db.users.insert_one({"name": "name"})