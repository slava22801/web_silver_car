from fastapi import APIRouter, Depends, HTTPException
from database.db_init import db
from auth import utils as auth_utils
from Schemas.schemas import TokenInfo, UserSchema, AutoInfo


admin_router = APIRouter(prefix="/admin")


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
def auth_admin_issue_jwt(auto:AutoInfo,
):
    car_data = auto.model_dump()
    db.cars.insert_one(
        {
            "name": car_data["name"],
            "price": car_data["price"],
            "mileage": car_data["mileage"],
            "engine": car_data["engine"],
            "transmition_box": car_data["transmition_box"],
            "gear": car_data["gear"],
            "rudder": car_data["rudder"],
            "carcase": car_data["carcase"],
            "color": car_data["color"]
         } 
    ) 
    return {"ok"}
    
# @admin_router.get("/get_all_cars")
# async def get_cars():
#     try:
#         cars = db.cars.find().to_list(length=100)
        

        
#         return cars
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    