from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from .given_title import GivenTitle
from .inevitable_title import InevitableTitle


class GivenInevitableTitle(GivenTitle):
    __tablename__ = f"{Base.TABLENAME_PREFIX}given_inevitable_titles"

    title_id = Column(
        Integer,
        ForeignKey(InevitableTitle.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    title = relationship("InevitableTitle")

    streak_length = Column(Integer, nullable=False, default=1)

    def __repr__(self):
        return (
            "<GivenInevitableTitle("
            f"participant_id={self.participant_id}, "
            f"title_id={self.title_id}, "
            f'given_on="{self.given_on}", '
            f'streak_length="{self.streak_length}"'
            ")>"
        )
