from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    title: str =Field(..., max_length=120)
    content: str
    post_type: str ="post"

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    user_id: int
    likes_count: int
    dislikes_count: int =0
    comments_count: int =0
    created_at: datetime

    class Confing:
        from_attributes = True



