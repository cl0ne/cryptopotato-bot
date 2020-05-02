from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from .group_chat import GroupChat


class ShuffledTitle(Base):
    __tablename__ = f'{Base.TABLENAME_PREFIX}shuffled_titles'

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey(GroupChat.chat_id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    text = Column(String(length=255), nullable=False)
    roll_order = Column(Integer, nullable=True, index=True)

    chat = relationship('GroupChat', back_populates='shuffled_titles')

    def __repr__(self):
        return ('<ShuffledTitle('
                f'chat_id={self.chat_id}, '
                f'text="{self.text}", '
                f'roll_order={self.roll_order}'
                ')>')
