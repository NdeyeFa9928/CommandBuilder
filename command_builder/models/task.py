from pydantic import BaseModel
from typing import List
from command_builder.models.command import Command


class Task(BaseModel):
    name: str
    description: str
    commands: List[Command]
