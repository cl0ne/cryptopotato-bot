from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base
from .inevitable_title import InevitableTitle
from .participant import Participant
from .utc_datetime import UTCDateTime


class AssignmentRecord(Base):
    __tablename__ = f'{Base.TABLENAME_PREFIX}assignment_records'
    __table_args__ = (
        UniqueConstraint('participant_id', 'title_id'),
    )

    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey(Participant.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    participant = relationship('Participant')

    title_id = Column(Integer, ForeignKey(InevitableTitle.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    title = relationship('InevitableTitle')

    count = Column(Integer, nullable=False, default=0)
    last_assigned_on = Column(UTCDateTime)

    def __repr__(self):
        return ('<AssignmentRecord('
                f'participant_id={self.participant_id}, '
                f'title_id={self.title_id}, '
                f'count={self.count}, '
                f'last_assigned_on="{self.last_assigned_on}"'
                ')>')
