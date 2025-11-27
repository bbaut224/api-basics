from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users" 

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)                  
    email = Column(String, unique=True, index=True)    
    password_hash = Column(String)

    posts = relationship("Post", back_populates="owner")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)

    
    # Сразу задаём default=0, чтобы новый пост начинался с нуля лайков
    likes = Column(Integer, default=0)

    # Внешний ключ — пользователь, который создал пост
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Связь с владельцем поста
    owner = relationship("User", back_populates="posts")