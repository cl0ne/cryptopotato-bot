from sqlalchemy import Column, Integer

from .title import TitleFromGroupChat, Base


class ShuffledTitle(TitleFromGroupChat):
    __tablename__ = f"{Base.TABLENAME_PREFIX}shuffled_titles"
    __group_chat_back_populates__ = "shuffled_titles"

    roll_order = Column(Integer, nullable=True, index=True)

    def __repr__(self):
        return (
            "<ShuffledTitle("
            f"chat_id={self.chat_id}, "
            f'text="{self.text}", '
            f"roll_order={self.roll_order}"
            ")>"
        )
