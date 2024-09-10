from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    telegram_id: int
    username: str
    locale: Optional[str] = "ru"