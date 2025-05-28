import base64
import pickle
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from core import AppContext

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True, nullable=False)
    face_embedding = Column(String, nullable=False)  # Stored as base64/pickle string

    def decode_embedding(
        self,
    ):
        return pickle.loads(base64.b64decode(self.face_embedding.encode("utf-8")))


class UserRepository:
    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.db = ctx.db

    def add_user(self, user_name, face_embedding):
        self.db.create(Users(user_name=user_name, face_embedding=face_embedding))

    def get_by_name(self, user_name):
        return self.db.find(Users, user_name=user_name)

    def get_all(
        self,
    ) -> list[Users]:
        return self.db.get_all(Users)
