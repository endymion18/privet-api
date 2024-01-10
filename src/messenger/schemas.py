import uuid

from src.messenger.models import Chat, Message


class GetChatSchema:
    chat_id: int
    chat_with: uuid.UUID
    chat_with_name: str
    last_message: Message

    def __init__(self,
                 current_user_id: uuid.UUID,
                 chat_info: Chat,
                 first_user_name: str,
                 second_user_name: str,
                 last_message: Message):
        self.chat_id = chat_info.id

        if chat_info.first_user == current_user_id:
            self.chat_with = chat_info.second_user
            self.chat_with_name = second_user_name

        if chat_info.second_user == current_user_id:
            self.chat_with = chat_info.first_user
            self.chat_with_name = first_user_name

        self.last_message = last_message
