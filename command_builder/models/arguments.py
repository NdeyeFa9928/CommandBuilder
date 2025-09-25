from pydantic import BaseModel


class Argument(BaseModel):
    code: str
    name: str
    description: str
