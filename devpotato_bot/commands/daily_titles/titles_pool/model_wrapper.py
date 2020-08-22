from enum import Enum
from typing import Optional, Union, List, Iterable, Type

from sqlalchemy import literal
from sqlalchemy.orm import Session, Query

from devpotato_bot.commands.daily_titles import models

DEFAULTS_POOL_ID = object()
TITLE_LENGTH_LIMIT = 255
PAGE_SIZE = 12

_MODEL_TYPES = Union[
    models.TitleTemplate,
    models.InevitableTitle,
    models.ShuffledTitle
]


class TitleType(Enum):
    INEVITABLE = ('inevitable', models.InevitableTitle)
    SHUFFLED = ('shuffled', models.ShuffledTitle)

    def __new__(cls, value: str, model_type):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.model_type = model_type
        return obj

    @classmethod
    def from_prefix(cls, prefix) -> 'TitleType':
        return next((t for t in cls if t.value.startswith(prefix)), None)

    def _base_query(self, session: Session, pool_id: Optional[int]) -> (Type[_MODEL_TYPES], Query):
        if pool_id is DEFAULTS_POOL_ID:
            model_type = models.TitleTemplate
            filter_by = dict(is_inevitable=(self == TitleType.INEVITABLE))
        else:
            model_type = self.model_type
            filter_by = dict(chat_id=pool_id)
        q = session.query(model_type).filter_by(**filter_by)
        return model_type, q

    def get_title(self, session: Session, pool_id: Optional[int], title_id: int) -> Optional[_MODEL_TYPES]:
        model_type, q = self._base_query(session, pool_id)
        return q.filter(model_type.id == title_id).one_or_none()

    def query_select(self, session: Session, pool_id: Optional[int]) -> Query:
        model_type, q = self._base_query(session, pool_id)
        return q.order_by(model_type.id)

    def delete(self, session: Session, pool_id: Optional[int], ids: Optional[List[int]] = None) -> int:
        model_type, q = self._base_query(session, pool_id)
        if ids is not None:
            q = q.filter(model_type.id.in_(ids))
        return q.delete(synchronize_session=False)

    def copy_defaults(self, session: Session, pool_id: int) -> int:
        assert pool_id is not DEFAULTS_POOL_ID
        select_columns = (models.TitleTemplate.text, literal(pool_id).label('chat_id'))
        is_inevitable = self == TitleType.INEVITABLE
        source_query = session.query(*select_columns).filter_by(is_inevitable=is_inevitable)
        target_model = self.model_type
        insert_columns = [target_model.text, target_model.chat_id]
        ins = target_model.__table__.insert().from_select(insert_columns, source_query)
        return session.execute(ins).rowcount

    def add_list(self, session: Session, pool_id: Optional[int], titles: Iterable[str]):
        if pool_id is DEFAULTS_POOL_ID:
            model_type = models.TitleTemplate
            mapping_kwargs = {'is_inevitable': self == TitleType.INEVITABLE}
        else:
            model_type = self.model_type
            mapping_kwargs = {'chat_id': pool_id}
        mapped_titles = (dict(text=t, **mapping_kwargs) for t in titles)
        session.bulk_insert_mappings(model_type, mapped_titles)


def paginate_query(query: Query, page: int = 1, page_count: Optional[int] = None) -> (list, int, int):
    if page < 0 or (page_count and page_count < 0):
        raise ValueError('page and page count values should be non-negative')
    if page_count is None or page == page_count:
        title_count = query.count()
        page_count = 1 + (title_count - 1) // PAGE_SIZE
        page = min(page, page_count)
    if page_count == 0:
        return [], page, page_count
    last_index = page * PAGE_SIZE
    first_index = last_index - PAGE_SIZE
    titles = query[first_index:last_index]
    if not titles:
        return paginate_query(query, page)
    return titles, page, page_count
