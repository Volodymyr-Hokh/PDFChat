from typing import Optional

from pydantic import BaseModel, EmailStr
from src.enums import Role


class User(BaseModel):
    email: EmailStr


class UserCreate(User):
    password: str


class UserResponse(UserCreate):
    id: int


class Token(BaseModel):
    access_token: str


class Document(BaseModel):
    name: str
    file_path: str
    user_id: int


class Chat(BaseModel):
    name: Optional[str] = None
    document_id: int
    user_id: int


class Message(BaseModel):
    chat_id: int
    role: Optional[Role] = None
    content: str
