from fastapi import WebSocket
from src.messenger.models import *


class Connection:
    def __init__(self, user_id: uuid.UUID, websocket: WebSocket):
        self.user_id = user_id
        self.websocket = websocket


class WSManager:
    def __init__(self):
        self.active_connections: list[Connection] = []

    def add_connection(self, user_id: uuid.UUID, websocket: WebSocket):
        new_connection = Connection(user_id, websocket)
        self.active_connections.append(new_connection)

    def remove_connection(self, websocket: WebSocket):
        needed_connection = None
        for connection in self.active_connections:
            if connection.websocket == websocket:
                needed_connection = connection
        if needed_connection is not None:
            self.active_connections.remove(needed_connection)

    def proceed_request(self, req_type: str, user_id: uuid.UUID,
                        chat_id: uuid.UUID, text: str = ""):
        if req_type == "send_message":
            for connection in self.active_connections:
                if connection.user_id == user_id:
                    connection.websocket.send_json({"type": "new_message",
                                                    "chat_id": chat_id,
                                                    "from_id": user_id,
                                                    "text": text})
