from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    
    username: str
    password: str
    email: EmailStr
    role: str
    orders: dict
    
    
class TokenInfo(BaseModel):
    access_token: str
    token_type: str
    
    
class AutoInfo(BaseModel):
    name: str
    price: int
    mileage: int
    engine: str
    transmition_box: str
    gear: str
    rudder: str
    carcase: str
    color: str
    
class OrderInfo(BaseModel):
    from_id: str
    name: str
    auto_name: str
    number: str
    comment: str