from fastapi import FastAPI
from routes.users import users_router
from routes.cars import cars_router




main = FastAPI()

main.include_router(users_router)
main.include_router(cars_router)