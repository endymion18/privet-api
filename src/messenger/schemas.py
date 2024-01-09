import uuid

from src.messenger.models import Chat, Message


class GetChatSchema:
    chat_id: int
    first_user: uuid.UUID
    first_user_name: str
    second_user: uuid.UUID
    second_user_name: str
    last_message: Message

    def __init__(self,
                 chat_info: Chat,
                 first_user_name: str,
                 second_user_name: str,
                 last_message: Message):
        self.chat_id = chat_info.id
        self.first_user = chat_info.first_user
        self.first_user_name = first_user_name
        self.second_user = chat_info.second_user
        self.second_user_name = second_user_name
        self.last_message = last_message
