# app/models/message.py
from db.db import db

from typing import List

from peewee import (
    Model, CharField, TextField,
    DateTimeField,
)
from datetime import datetime
import os


# Define allowed roles
ROLE_CHOICES = ('user', 'bot')

class BaseModel(Model):
    class Meta:
        database = db

class Message(BaseModel):
    sess_id = CharField()
    user_id = CharField()
    role = CharField(choices=[(r, r) for r in ROLE_CHOICES])
    message = TextField()
    create_time = DateTimeField(default=datetime.now)
    create_date = DateTimeField(default=lambda: datetime.now().date())

    class Meta:
        table_name = "messages"


# rag_terminal_app.postgres_db_store


class MessageService:
    def __init__(self,db):
        self.db =db
        self.db.create_tables([Message], safe=True)
    @classmethod
    def save_message(cls,sess_id: str, user_id: str, role: str, message: str) -> Message:
        if role not in ("user", "bot"):
            raise ValueError("Role must be either 'user' or 'bot'")

        return Message.create(sess_id=sess_id, user_id=user_id, role=role, message=message)

    @classmethod
    def get_messages(cls,sess_id: str,user_id: str, limit: int = 10) -> List[Message]:
        query = (
            Message.select().where(
                (Message.sess_id == sess_id) & (Message.user_id == user_id)
            )
            .order_by(Message.create_time.desc())
            .limit(limit)
        )

        return list(reversed(query))
message_service_object=MessageService(db)