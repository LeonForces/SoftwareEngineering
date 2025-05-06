from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SFolderCreate(BaseModel):
    name: str


class SFolder(SFolderCreate):
    created_at: datetime
    updated_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
