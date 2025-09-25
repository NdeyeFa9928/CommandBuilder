from pydantic import BaseModel
from typing import Optional


class Argument(BaseModel):
    code: str
    name: str
    description: Optional[str] = ""
