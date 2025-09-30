from pydantic import BaseModel
from typing import List
from command_builder.models.task import Task


class Pipeline(BaseModel):
    name: str
    description: str
    tasks: List[Task]
