from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    
    username: str
    password: str
    email: EmailStr
    role: str = "user"
    
    
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
    email: EmailStr
    name: str
    auto_name: str
    number: str
    comment: str
    status: str = "В ожидании"

class ChangePasswordSchema(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str

class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str