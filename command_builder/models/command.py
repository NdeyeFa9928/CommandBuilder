from pydantic import BaseModel
from typing import List, Dict, Any


class Command(BaseModel):
    name: str
    description: str
    command: str
    arguments: List[Dict[str, Any]]
