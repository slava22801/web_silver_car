from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.orders import orders_router
from routes.users import users_router
from routes.cars import cars_router
from routes.admin import admin_router




main = FastAPI()
main.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://24silvercar.ru",
        "https://www.24silvercar.ru",
        "http://24silvercar.ru",
        "http://www.24silvercar.ru",
    ],  # React dev server и production домен
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

main.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

main.include_router(users_router)
main.include_router(cars_router)
main.include_router(admin_router)
main.include_router(orders_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:main", host="0.0.0.0", port=8001, reload=True)