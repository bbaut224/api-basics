from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio

from .database import get_db
from .models import Post, User
from .schemas import PostBase
from .auth import get_current_user  # функция для получения текущего пользователя

app = FastAPI()

# ConnectionManager управляет всеми клиентами, которые слушают лайки через WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # При подключении принимаем соединение и добавляем его в список
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        # При отключении удаляем соединение
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Рассылаем JSON всем подключённым клиентам
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/likes")
async def websocket_likes(websocket: WebSocket):
    """
    Этот endpoint слушает всех клиентов, которые хотят видеть лайки в реальном времени.
    Браузер подключается и слушает обновления.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Ждём любые сообщения от клиента (например, ping)
            # Можно использовать для расширения функционала
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Увеличиваем количество лайков поста на 1.
    Отправляем обновление всем WebSocket клиентам.
    """

    # Находим пост по ID
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 🔹 увеличиваем лайки
    post.likes += 1
    db.commit()
    db.refresh(post)  # обновляем объект ORM

    # 🔹 уведомляем всех WebSocket клиентов
    # Используем asyncio.create_task, чтобы не блокировать основной поток
    asyncio.create_task(
        manager.broadcast({"post_id": post_id, "likes": post.likes})
    )

    # Возвращаем результат пользователю
    return {"message": "Liked", "likes": post.likes}
