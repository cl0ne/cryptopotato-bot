from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from sqlalchemy import tuple_
from telegram import error, ChatMember
from telegram.utils.helpers import escape_markdown, mention_markdown

from ._strings import STREAK_MARK
from .models import GivenInevitableTitle
from .models import GivenShuffledTitle
from .models import InevitableTitle
from .models import ShuffledTitle
from .models.title import TitleFromGroupChat
from ...sample import sample_items_inplace

if TYPE_CHECKING:
    from datetime import datetime
    from typing import List, Tuple, Union, Optional, Dict, Iterable
    from sqlalchemy.orm import Session
    from telegram import Chat, User
    from .models import GroupChat

    ParticipantIDPairs = List[Tuple[int, int]]

SHUFFLED_TITLES_TO_GIVE = 5


class MissingUserWrapper:
    def __init__(self, user_id):
        self.user_id = user_id
        self.full_name = ""

    def mention_markdown_v2(self):
        return mention_markdown(self.user_id, self.full_name, version=2)


if TYPE_CHECKING:
    ParticipantFormatter = Union[User, MissingUserWrapper]


def assign_titles(
    session: Session, chat_data: GroupChat, tg_chat: Chat, trigger_time: datetime
):
    chat_data.name = tg_chat.title
    new_titles = _choose_new_titles(chat_data)
    if new_titles is None:
        chat_data.last_titles_plain, chat_data.last_titles = None, None
    else:
        inevitable, shuffled = new_titles
        _save_given_inevitable_titles(
            session, trigger_time, chat_data.last_triggered, inevitable
        )
        _save_given_shuffled_titles(session, trigger_time, shuffled)
        _refresh_user_data(tg_chat, chat_data, new_titles)
        new_texts = _build_titles_text(inevitable, shuffled)
        chat_data.last_titles_plain, chat_data.last_titles = new_texts
    chat_data.last_triggered = trigger_time
    session.commit()


TitleT = TypeVar("TitleT", bound=TitleFromGroupChat)


class NewTitles(Generic[TitleT]):
    def __init__(self, titles: List[TitleT], participant_id_pairs: ParticipantIDPairs):
        assert len(titles) == len(participant_id_pairs)
        self.titles: List[TitleT] = titles
        self.participant_id_pairs = participant_id_pairs
        self.tg_users: List[ParticipantFormatter] = []

    def is_empty(self) -> bool:
        return len(self.participant_id_pairs) == 0

    def get_title_ids(self) -> Iterable[int]:
        return (i.id for i in self.titles)

    def get_tg_user_ids(self) -> Iterable[int]:
        return (i for _, i in self.participant_id_pairs)

    def get_participant_ids(self) -> Iterable[int]:
        return (i for i, _ in self.participant_id_pairs)

    def format_lines(self, lines_plain: list, lines_mention: list):
        for title, user in zip(self.titles, self.tg_users):
            user_name = escape_markdown(user.full_name, version=2)
            title_text = escape_markdown(title.text, version=2)
            lines_plain.append(f" {user_name} \\- {title_text}")
            lines_mention.append(f" {user.mention_markdown_v2()} \\- {title_text}")


class NewInevitableTitles(NewTitles[InevitableTitle]):
    def __init__(
        self, titles: List[InevitableTitle], participant_id_pairs: ParticipantIDPairs
    ):
        super().__init__(titles, participant_id_pairs)
        self.records: List[GivenInevitableTitle] = []

    @staticmethod
    def _format_streak_marks(streak_length: int):
        if streak_length < 2:
            return ""
        return f"{streak_length}x{STREAK_MARK} "

    def format_lines(self, lines_plain: list, lines_mention: list):
        for title, user, record in zip(self.titles, self.tg_users, self.records):
            user_name = escape_markdown(user.full_name, version=2)
            title_text = escape_markdown(title.text, version=2)
            streak_mark = self._format_streak_marks(record.streak_length)
            lines_plain.append(f" {streak_mark}{user_name} \\- {title_text}")
            lines_mention.append(
                f" {streak_mark}{user.mention_markdown_v2()} \\- {title_text}"
            )


NewShuffledTitles = NewTitles[ShuffledTitle]


def _choose_new_titles(
    chat: GroupChat,
) -> Optional[Tuple[NewInevitableTitles, NewShuffledTitles]]:
    participant_ids = chat.get_participant_ids()
    participant_count = len(participant_ids)
    if not participant_count:
        return None

    inevitable_titles: List[InevitableTitle] = chat.inevitable_titles[
        :participant_count
    ]
    inevitable_titles_count = len(inevitable_titles)
    shuffled_titles_needed = min(
        participant_count - inevitable_titles_count, SHUFFLED_TITLES_TO_GIVE
    )
    shuffled_titles = chat.dequeue_shuffled_titles(shuffled_titles_needed)
    shuffled_titles_count = len(shuffled_titles)

    sample_size = shuffled_titles_count + inevitable_titles_count
    sample_items_inplace(participant_ids, sample_size)

    first_shuffled_title = -inevitable_titles_count - 1
    return (
        NewInevitableTitles(
            inevitable_titles, participant_ids[:first_shuffled_title:-1]
        ),
        NewShuffledTitles(
            shuffled_titles,
            participant_ids[first_shuffled_title : -sample_size - 1 : -1],
        ),
    )


def _save_given_inevitable_titles(
    session: Session,
    given_on: datetime,
    old_given_on: Optional[datetime],
    new_titles: NewInevitableTitles,
):
    """Calculates new streak lengths and adds new given inevitable titles to database"""
    if old_given_on is None:
        previous_streaks = None
    else:
        previous_streaks = _load_old_streaks(session, old_given_on, new_titles)
    for participant_id, title in zip(
        new_titles.get_participant_ids(), new_titles.titles
    ):
        new_streak_length = 1
        if previous_streaks:
            new_streak_length += previous_streaks.get(participant_id, 0)
        record = GivenInevitableTitle(
            participant_id=participant_id,
            title=title,
            given_on=given_on,
            streak_length=new_streak_length,
        )
        new_titles.records.append(record)
        session.add(record)


def _load_old_streaks(
    session: Session, old_given_on: datetime, records_filter: NewInevitableTitles
) -> Dict[int, int]:
    query = session.query(
        GivenInevitableTitle.participant_id, GivenInevitableTitle.streak_length
    ).filter(
        tuple_(GivenInevitableTitle.participant_id, GivenInevitableTitle.title_id).in_(
            zip(records_filter.get_participant_ids(), records_filter.get_title_ids())
        ),
        GivenInevitableTitle.given_on == old_given_on,
    )
    return dict(query)


def _save_given_shuffled_titles(
    session: Session,
    given_on: datetime,
    new_titles: NewShuffledTitles,
):
    """Adds new given shuffled titles to database"""
    for participant_id, title in zip(
        new_titles.get_participant_ids(), new_titles.titles
    ):
        record = GivenShuffledTitle(
            participant_id=participant_id, title=title, given_on=given_on
        )
        session.add(record)


def _refresh_user_data(tg_chat: Chat, chat: GroupChat, new_titles: Iterable[NewTitles]):
    """Gets current names and usernames of participants, updates database with this data and participation status"""
    if all(map(NewTitles.is_empty, new_titles)):
        return
    participants_new_data, load_from_db = [], {}
    for title_set in new_titles:
        for participant_id, user_id in title_set.participant_id_pairs:
            new_user_data = dict(id=participant_id)
            try:
                member = tg_chat.get_member(user_id)
                user = member.user
                new_user_data.update(full_name=user.full_name, username=user.username)
                if member.status in (ChatMember.KICKED, ChatMember.LEFT):
                    new_user_data.update(is_active=False)
                participants_new_data.append(new_user_data)
            except error.BadRequest as ex:
                if ex.message == "User not found":
                    new_user_data.update(is_active=False, is_missing=True)
                    participants_new_data.append(new_user_data)
                user = MissingUserWrapper(user_id)
                load_from_db[participant_id] = user
            title_set.tg_users.append(user)

    session: Session = Session.object_session(chat)
    from .models import Participant

    session.bulk_update_mappings(Participant, participants_new_data)
    session.commit()
    loaded_names = (
        session.query(Participant.id, Participant.full_name)
        .filter(Participant.id.in_(load_from_db))
        .all()
    )
    for participant_id, participant_name in loaded_names:
        load_from_db[participant_id].full_name = participant_name


def _build_titles_text(
    inevitable_titles: NewInevitableTitles,
    shuffled_titles: NewShuffledTitles,
) -> Tuple[str, str]:
    lines_mention, lines_plain = [], []  # type: List[str], List[str]

    inevitable_titles.format_lines(lines_plain, lines_mention)
    if not (inevitable_titles.is_empty() or shuffled_titles.is_empty()):
        lines_plain.append("")
        lines_mention.append("")
    shuffled_titles.format_lines(lines_plain, lines_mention)

    return "\n".join(lines_plain), "\n".join(lines_mention)
