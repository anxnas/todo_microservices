from pydantic import BaseModel
from typing import Optional

class TaskInfo(BaseModel):
    id: str
    title: str

class CommentBase(BaseModel):
    content: str
    task_id: str
    user_id: int

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    task: Optional[TaskInfo] = None

    class Config:
        orm_mode = True