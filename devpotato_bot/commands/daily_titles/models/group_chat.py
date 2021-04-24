from __future__ import annotations

import random
from typing import TYPE_CHECKING

from sqlalchemy import Column, BigInteger, Boolean, Integer, String, Text, false
from sqlalchemy.orm import relationship, Session

from .base import Base
from .utc_datetime import UTCDateTime

if TYPE_CHECKING:
    from typing import Optional, List, Tuple
    from . import Participant, ShuffledTitle, InevitableTitle


class GroupChat(Base):
    __tablename__ = f'{Base.TABLENAME_PREFIX}group_chats'

    chat_id = Column(BigInteger, primary_key=True)
    name = Column(String(length=255), nullable=False)
    is_enabled = Column(Boolean(create_constraint=True), nullable=False)
    is_migration_conflicted = Column(
        Boolean(create_constraint=True), nullable=False, default=False, server_default=false()
    )
    last_triggered = Column(UTCDateTime)
    last_given_titles_count = Column(Integer)

    participants = relationship('Participant', back_populates='chat', lazy='dynamic')
    inevitable_titles = relationship('InevitableTitle', back_populates='chat', lazy='dynamic')
    shuffled_titles = relationship('ShuffledTitle', back_populates='chat', lazy='dynamic')

    @classmethod
    def get_by_id(cls, session, chat_id) -> Optional[GroupChat]:
        return session.query(GroupChat).filter_by(chat_id=chat_id).one_or_none()

    def get_participant(self, user_id) -> Optional[Participant]:
        return self.participants.filter_by(user_id=user_id).one_or_none()

    def get_participants_ordered(self, ordered_ids: List[int]) -> List[Participant]:
        session: Session = Session.object_session(self)
        from .participant import Participant
        query = session.query(
            Participant
        ).filter(
            Participant.id.in_(ordered_ids)
        )
        participants_map = {p.id: p for p in query.all()}
        return [participants_map[i] for i in ordered_ids]

    def get_participant_ids(self) -> List[int]:
        session: Session = Session.object_session(self)
        from .participant import Participant
        query = session.query(
            Participant.id
        ).filter(
            Participant.is_active,
            Participant.chat == self
        ).order_by(
            Participant.id
        )
        return [i for (i, ) in query]

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
                f'last_given_titles_count="{self.last_given_titles_count}"'
                ')>')
