from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    content: str

class PostOut(BaseModel):
    id: int
    content: str
    likes: int
    user_id: int
    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str
    content: str

