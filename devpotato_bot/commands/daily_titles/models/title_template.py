from sqlalchemy import Column, Integer, String, Boolean

from .base import Base


class TitleTemplate(Base):
    __tablename__ = f'{Base.TABLENAME_PREFIX}title_templates'

    id = Column(Integer, primary_key=True)
    text = Column(String(length=255), nullable=False)
    is_inevitable = Column(Boolean, nullable=False)

    def __repr__(self):
        return ('<TitleTemplate('
                f'id={self.chat_id}, '
                f'text="{self.text}", '
                f'is_inevitable="{self.is_inevitable}"'
                ')>')
