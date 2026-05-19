from pydantic import BaseModel, Field ,HttpUrl ,model_validator
from typing import Optional , List , Any ,Dict
from datetime import datetime
from enum import Enum
from src.api.response_models.schemas.user import UserMinInfo


class PostType(str, Enum):
    THOUGHT = "Thought"
    MEDIA = "Media"
    PORTFOLIO = "Portfolio"
    ARTICLE = "Article"


class PostBase(BaseModel):
    title: Optional[str] = Field(None,min_length=3,max_length=150)
    content:str=Field(...,min_length=3)
    post_type:PostType = PostType.THOUGHT
    image_url:Optional[str]=None
    extra_data:Dict[str,Any]= Field(default_factory=dict)
    is_published: bool = True


class PostCreate(PostBase):
    tags: Optional[List[str]] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_extra_data_based_on_type(self):
        post_type = self.post_type
        extra_data = self.extra_data

        if post_type == PostType.PORTFOLIO:
            if "github_link" not in extra_data and "demo_url" not in extra_data:
                raise ValueError("برای پست‌های پورتفولیو، حداقل لینک گیت‌هاب یا دمو الزامی است")

        elif post_type == PostType.ARTICLE:
            if not self.title or len(self.title) < 10:
                raise ValueError("مقالات تخصصی باید عنوانی حداقل با ۱۰ کاراکتر داشته باشند")

        return self


class PostResponse(PostBase):
    id:int
    user_id:int
    likes_count:int
    comments_count:int
    view_count:int
    created_at:datetime
    updated_at:datetime

    class Config:
        from_attributes = True


class PostWithUserResponse(PostResponse):
    author:UserMinInfo


class PostListResponse(BaseModel):
    items : list[PostWithUserResponse]
    total_count :int
    page : int
    size : int
    total_pages: int

class MyPostListResponse(BaseModel):
    items : list[PostResponse]
    total_count: int
    page: int
    size: int
    total_pages: int


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=150)
    content: Optional[str] = Field(None, min_length=3)
    post_type: Optional[PostType] = None
    image_url: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None
    tags: Optional[List[str]] = None


