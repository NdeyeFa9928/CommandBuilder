from pydantic import BaseModel
from typing import List, Dict, Any

class Pipeline(BaseModel):
    name: str
    description: str
    tasks: List[Dict[str, Any]]



