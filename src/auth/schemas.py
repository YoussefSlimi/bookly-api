from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from src.books.schemas import BookModel
from src.reviews.schemas import ReviewModel
import uuid
from typing import List, Optional


class UserCreateModel(BaseModel) :
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=6)
    admin_key: Optional[str] = None

class AdminCreateModel(UserCreateModel):
    pass

class UserModel(BaseModel) :
    uid: uuid.UUID 
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_verified: bool = Field(default= False)
    password_hash: str 
    created_at: datetime
    updated_at: datetime

class UserPublicModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_verified: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime

class UserBooksModel(UserModel):
    books: list[BookModel]
    reviews: List[ReviewModel]

class UserLoginModel(BaseModel) :
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=6)

class EmailModel(BaseModel):
    addresses: List[EmailStr]

class PasswordResetRequestModel(BaseModel) :
    email: EmailStr = Field(max_length=40)

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str

class UserRoleUpdateModel(BaseModel):
    role: str = Field(pattern="^(admin|user)$")