from fastapi import WebSocket, Depends, Query
from src.messenger.models import *
from src.database import get_async_session
from sqlalchemy import select
from src.auth.models import User
import os
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session_maker

secret_key = os.environ.get("SECRET_KEY")


async def websocket_auth(websocket: WebSocket, token: str = Query(...)):
    try:
        decoded_token = jwt.decode(token, secret_key, ["HS256"])

        email = decoded_token.get("sub")
        return email
    except JWTError:
        await websocket.send_text("Token auth fail")
        await websocket.close()


class Connection:
    def __init__(self, user_id: uuid.UUID, websocket: WebSocket):
        self.user_id = user_id
        self.websocket = websocket


class WSManager:
    def __init__(self):
        self.active_connections: list[Connection] = []
        # в будущем мб поменять это на dict[user_uuid:websocket]

    async def add_connection(self, websocket: WebSocket,
                             token: str):
        await websocket.accept()
        result = await websocket_auth(websocket, token)
        if result is None:
            return
        async with async_session_maker() as session:
            stmt = await session.execute(select(User).where(User.email == result))
            current_user = stmt.scalar()
            new_connection = Connection(current_user.id, websocket)
            await websocket.send_text("connection success")
            self.active_connections.append(new_connection)
            return current_user

    def remove_connection(self, websocket: WebSocket):
        needed_connection = None
        for connection in self.active_connections:
            if connection.websocket == websocket:
                needed_connection = connection
        if needed_connection is not None:
            self.active_connections.remove(needed_connection)

    async def send_message(self, req_type: str, user_id: uuid.UUID,
                           chat_id: uuid.UUID, text: str = ""):
        async with async_session_maker() as session:
            stmt = await session.execute(select(Chat).where(Chat.id == chat_id))
            chat = stmt.scalar()
            for connection in self.active_connections:
                if connection.user_id == chat.first_user \
                        or connection.user_id == chat.second_user:
                    await connection.websocket.send_json({"type": "new_message",
                                                          "chat_id": str(chat_id),
                                                          "from_id": str(user_id),
                                                          "text": text})


manager = WSManager()
