from pydantic import BaseModel
from typing import Optional, Any


class Argument(BaseModel):
    code: str
    name: str
    description: Optional[str] = ""
    type: Optional[str] = "string"
    required: Optional[int] = 0
    default: Optional[str] = ""
    validation: Optional[dict[str, Any]] = None
