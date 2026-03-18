from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from fastapi_blog.constants import MAX_AUTHOR_LENGTH, MAX_TITLE_LENGTH


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=MAX_AUTHOR_LENGTH)


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: datetime
