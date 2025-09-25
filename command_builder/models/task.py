from pydantic import BaseModel
from typing import List, Dict, Any


class Task(BaseModel):
    name: str
    description: str
    commands: List[Dict[str, Any]]
