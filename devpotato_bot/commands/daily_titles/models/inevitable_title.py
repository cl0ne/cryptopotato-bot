from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .group_chat import GroupChat

from .title import TitleFromGroupChat, Base


class InevitableTitle(TitleFromGroupChat):
    __tablename__ = f'{Base.TABLENAME_PREFIX}inevitable_titles'
    __group_chat_back_populates__ = 'inevitable_titles'

    def __repr__(self):
        return ('<InevitableTitle('
                f'chat_id={self.chat_id}, '
                f'text="{self.text}"'
                ')>')
