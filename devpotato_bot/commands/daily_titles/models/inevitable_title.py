
from .title import TitleFromGroupChat, Base


class InevitableTitle(TitleFromGroupChat):
    __tablename__ = f'{Base.TABLENAME_PREFIX}inevitable_titles'
    __group_chat_back_populates__ = 'inevitable_titles'

    def __repr__(self):
        return ('<InevitableTitle('
                f'chat_id={self.chat_id}, '
                f'text="{self.text}"'
                ')>')
