from pydantic import BaseModel
from datetime import datetime
from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel
from typing import List, Optional
import uuid
class BookModel(BaseModel) :
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    language: str
    created_at: datetime
    updated_at: datetime

class BookDetailModel(BookModel) :
    reviews: List[ReviewModel]
    tags: List[TagModel]


class BookCreateModel(BaseModel) :
    title: str
    author: str
    publisher: str
    language: str
    


class UpdateBookModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[str] = None

class BookResponseModel(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    language: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True