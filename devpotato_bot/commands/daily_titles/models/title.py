from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from .base import Base
from .group_chat import GroupChat


class Title(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    text = Column(String(length=255), nullable=False)


class TitleFromGroupChat(Title):
    __abstract__ = True

    @declared_attr
    def chat_id(cls):
        return Column(
            BigInteger,
            ForeignKey(GroupChat.chat_id, onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )

    @declared_attr
    def chat(cls):
        return relationship(
            "GroupChat", back_populates=cls.__group_chat_back_populates__
        )
