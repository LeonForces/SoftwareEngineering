from pydantic import BaseModel, ConfigDict


class SEmail(BaseModel):
    recipient: str
    header: str
    description: str

    model_config = ConfigDict(from_attributes=True)
