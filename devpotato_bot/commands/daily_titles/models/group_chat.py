from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union, Type

if TYPE_CHECKING:
    from . import InevitableTitle, Participant, ShuffledTitle

import random
from typing import List, Tuple

from sqlalchemy import Column, String, BigInteger, Boolean, Text, false, literal
from sqlalchemy.orm import relationship, Session

from .base import Base
from .utc_datetime import UTCDateTime


class GroupChat(Base):
    __tablename__ = f'{Base.TABLENAME_PREFIX}group_chats'

    chat_id = Column(BigInteger, primary_key=True)
    name = Column(String(length=255), nullable=False)
    is_enabled = Column(Boolean, nullable=False)
    is_migration_conflicted = Column(Boolean, nullable=False, default=False, server_default=false())
    last_triggered = Column(UTCDateTime)
    last_titles = Column(Text)
    last_titles_plain = Column(Text)

    participants = relationship('Participant', back_populates='chat', lazy='dynamic')
    inevitable_titles = relationship('InevitableTitle', back_populates='chat', lazy='dynamic')
    shuffled_titles = relationship('ShuffledTitle', back_populates='chat', lazy='dynamic')

    @classmethod
    def get_by_id(cls, session, chat_id) -> Optional[GroupChat]:
        return session.query(GroupChat).filter_by(chat_id=chat_id).one_or_none()

    def get_participant(self, user_id) -> Optional[Participant]:
        return self.participants.filter_by(user_id=user_id).one_or_none()

    def get_participant_ids(self) -> List[Tuple[int, int]]:
        session: Session = Session.object_session(self)
        from .participant import Participant
        return session.query(
            Participant.id, Participant.user_id
        ).filter(
            Participant.is_active, Participant.chat == self
        ).order_by(Participant.id).all()

    def dequeue_shuffled_titles(self, limit: int) -> List[ShuffledTitle]:
        if not limit:
            return []
        from . import ShuffledTitle
        query = self.shuffled_titles.filter(ShuffledTitle.roll_order.isnot(None))
        query = query.order_by(ShuffledTitle.roll_order)
        titles: List[ShuffledTitle] = query[:limit]
        title_count = len(titles)

        session: Session = Session.object_session(self)
        old_ids: List[Tuple[int]] = []
        if title_count < limit:
            query_old = session.query(ShuffledTitle.id).filter_by(chat=self)
            query_old = query_old.filter(ShuffledTitle.roll_order.is_(None))
            old_ids = query_old.all()

        for t in titles:
            t.roll_order = None
        if old_ids:
            new_queue = (
                dict(chat_id=self.chat_id, id=i, roll_order=random.randrange(2**16))
                for i, in old_ids
            )
            session.bulk_update_mappings(ShuffledTitle, new_queue)
            session.commit()

            remainder_limit = limit - title_count
            more_titles = query[:remainder_limit]
            for t in more_titles:
                t.roll_order = None
            titles += more_titles
        session.commit()
        return titles

    def __repr__(self) -> str:
        return ('<GroupChat('
                f'chat_id={self.chat_id}, '
                f'name="{self.name}", '
                f'is_enabled={self.is_enabled}, '
                f'last_triggered="{self.last_triggered}", '
                f'last_titles="{self.last_titles}", '
                f'last_titles_plain="{self.last_titles_plain}"'
                ')>')
