from pydantic import BaseModel
from typing import List, Dict, Any


class Argument(BaseModel):
    code: str
    name: str
    description: str

