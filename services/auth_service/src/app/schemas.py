from pydantic import BaseModel, ConfigDict
from typing import Optional


class SUser(BaseModel):
    username: str
    email: str
    hashed_password: str
    age: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
