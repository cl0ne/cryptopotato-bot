from sqlalchemy import Column, Integer, String, BigInteger, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import expression as expr
from sqlalchemy.orm import relationship

from .base import Base
from .group_chat import GroupChat


class Participant(Base):
    __tablename__ = f'{Base.TABLENAME_PREFIX}participants'
    __table_args__ = (
        UniqueConstraint('user_id', 'chat_id'),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, ForeignKey(GroupChat.chat_id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(length=255), nullable=False)
    username = Column(String(length=32), nullable=True)
    is_active = Column(Boolean, nullable=False)
    is_missing = Column(Boolean, nullable=False, default=False, server_default=expr.false())

    chat = relationship('GroupChat', back_populates='participants')

    def __repr__(self):
        return ('<Participant('
                f'user_id={self.user_id}, '
                f'chat_id={self.chat_id}, '
                f'full_name="{self.full_name}", '
                f'username="{self.full_name}", '
                f'is_active={self.is_active}, '
                f'is_missing={self.is_missing}'
                ')>')
