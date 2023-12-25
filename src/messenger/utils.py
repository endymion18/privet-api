from src.messenger.wsmanager import WSManager
from fastapi import WebSocket, Query
from jose import JWTError
import os
from jose import jwt


secret_key = os.environ.get("SECRET_KEY")
manager = WSManager()


async def websocket_auth(websocket: WebSocket, token: str = Query(...)):
    try:
        decoded_token = jwt.decode(token, secret_key, ["HS256"])

        email = decoded_token.get("sub")
        return email
    except JWTError:
        await websocket.send_text("Token auth fail")
        await websocket.close()
