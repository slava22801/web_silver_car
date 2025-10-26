from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    
    username: str
    password: str
    email: EmailStr
    
    
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