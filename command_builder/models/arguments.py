from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class ValidationRule(BaseModel):
    file_extensions: Optional[List[str]] = None


class Argument(BaseModel):
    code: str
    name: str
    description: str
    type: str
    required: int
    validation: Optional[ValidationRule] = None
