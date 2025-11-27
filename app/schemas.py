from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    content: str

class PostOut(PostBase):
    id: int
    likes: int
    author_id: int
    class Config:
        orm_mode = True
