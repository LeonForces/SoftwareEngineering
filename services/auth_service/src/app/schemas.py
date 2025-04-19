from pydantic import BaseModel
from typing import Optional


class SUser(BaseModel):
    username: str
    email: str
    hashed_password: str
    age: Optional[int] = None

    class Congig:
        orm_mode = True
