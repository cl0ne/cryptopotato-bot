from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from .given_title import GivenTitle
from .shuffled_title import ShuffledTitle


class GivenShuffledTitle(GivenTitle):
    __tablename__ = f"{Base.TABLENAME_PREFIX}given_shuffled_titles"

    title_id = Column(
        Integer,
        ForeignKey(ShuffledTitle.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    title = relationship("ShuffledTitle")

    def __repr__(self):
        return (
            "<GivenShuffledTitle("
            f"participant_id={self.participant_id}, "
            f"title_id={self.title_id}, "
            f'given_on="{self.given_on}"'
            ")>"
        )
