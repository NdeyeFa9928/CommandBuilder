from pydantic import BaseModel
from typing import List
from command_builder.models.arguments import Argument


class Command(BaseModel):
    name: str
    description: str
    command: str
    arguments: List[Argument]
