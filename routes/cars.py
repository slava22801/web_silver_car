from fastapi import APIRouter


cars_router = APIRouter(prefix="/cars")

@cars_router.get("/")
async def get_users():
    return {"cars"}