from fastapi import APIRouter, Depends
from database.db_init import db
from auth import utils as auth_utils
from Schemas.schemas import TokenInfo, UserSchema
from Schemas.user import usersEntity


users_router = APIRouter(prefix="/user")

@users_router.get("")
async def get_users():
    return usersEntity(db.users.find())

@users_router.post("/add_user")
async def add_user(user:UserSchema):
    
    user_data = user.model_dump()
    
    
    db.users.insert_one(
        {
            "username": user_data["username"],
            "password": user_data["password"],
            "email": user_data["email"],
            "role": user_data["role"]
         }
                        )
    
@users_router.post("/login")
async def auth_user_issue_jwt(
    user: UserSchema = Depends(auth_utils.validate_auth_user),
):
    jwt_payload = {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
    }
    token = auth_utils.encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer"
    )