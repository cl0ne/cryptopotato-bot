from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from .base import Base
from .participant import Participant
from .utc_datetime import UTCDateTime


class GivenTitle(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @declared_attr
    def participant_id(cls):
        # pylint: disable=no-self-argument
        return Column(
            Integer,
            ForeignKey(Participant.id, onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )

    @declared_attr
    def participant(cls):
        # pylint: disable=no-self-argument
        return relationship("Participant")

    given_on = Column(UTCDateTime, nullable=False)
