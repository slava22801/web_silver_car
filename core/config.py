from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent.parent

class AuthJWt(BaseModel):
    private_key_path: Path = BASE_DIR / "keys" / "private.pem"
    public_key_path: Path = BASE_DIR / "keys" / "public.pem"
    algorithm : str = "RS256"
    access_token_expire_minutes: int = 15
    
class Settings(BaseSettings):
    auth_jwt: AuthJWt = AuthJWt()
    
    
settings = Settings()