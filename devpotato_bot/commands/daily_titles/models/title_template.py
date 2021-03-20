from sqlalchemy import Column, Boolean

from .title import Title, Base


class TitleTemplate(Title):
    __tablename__ = f'{Base.TABLENAME_PREFIX}title_templates'

    is_inevitable = Column(Boolean(create_constraint=True), nullable=False)

    def __repr__(self):
        return ('<TitleTemplate('
                f'id={self.id}, '
                f'text="{self.text}", '
                f'is_inevitable="{self.is_inevitable}"'
                ')>')
