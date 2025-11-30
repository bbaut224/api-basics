from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio

from .database import Base, engine, get_db
from .models import User, Post
from .schemas import UserCreate, UserOut, PostBase, PostOut
from .auth import fake_hash, get_current_user
from .websocket_manager import ConnectionManager
from .chat_manager import chat_manager

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, schemas
from .chat_manager import chat_manager


app = FastAPI()

Base.metadata.create_all(bind=engine)

likes_manager = ConnectionManager()

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(username=user.username, password=fake_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "registered"}

@app.post("/posts", response_model=PostOut)
def create_post(data: PostBase, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    post = Post(title=data.title, content=data.content, author_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@app.get("/posts", response_model=list[PostOut])
def get_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()

@app.post("/posts/{post_id}/like")
async def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(404)

    post.likes += 1
    db.commit()
    db.refresh(post)

    asyncio.create_task(
        likes_manager.broadcast({"post_id": post_id, "likes": post.likes})
    )

    return {"likes": post.likes}

@app.websocket("/ws/likes")
async def ws_likes(websocket: WebSocket):
    await likes_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        likes_manager.disconnect(websocket)

@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: int):
    await chat_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            receiver = data["to"]
            msg = data["message"]
            await chat_manager.send_personal_message(receiver, {
                "from": user_id,
                "message": msg
            })
    except WebSocketDisconnect:
        chat_manager.disconnect(user_id, websocket)
