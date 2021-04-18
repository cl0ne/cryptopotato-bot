from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from sqlalchemy import tuple_
from sqlalchemy.orm import Session
from telegram import error, ChatMember

from .models import GivenInevitableTitle
from .models import GivenShuffledTitle
from .models import InevitableTitle
from .models import ShuffledTitle
from .models.title import TitleFromGroupChat
from ...sample import sample_items_inplace

if TYPE_CHECKING:
    from datetime import datetime
    from typing import List, Tuple, Optional, Dict, Iterable
    from telegram import Chat
    from .models import GroupChat

    from .models import Participant

SHUFFLED_TITLES_TO_GIVE = 5


def assign_titles(
        session: Session,
        chat_data: GroupChat,
        tg_chat: Chat,
        trigger_time: datetime
) -> Tuple[List[GivenInevitableTitle], List[GivenShuffledTitle]]:
    chat_data.name = tg_chat.title
    assignment = _choose_titles(chat_data)
    records = [], []
    if assignment is None:
        chat_data.last_given_titles_count = None
    else:
        (inevitable_titles, shuffled_titles, participants) = assignment
        refresh_user_data(participants, tg_chat)
        inevitable_titles_count = len(inevitable_titles)
        wrapper_inevitable = NewInevitableTitles(
            inevitable_titles,
            participants[:inevitable_titles_count]
        )
        wrapper_shuffled = NewShuffledTitles(
            shuffled_titles,
            participants[inevitable_titles_count:]
        )
        records = (
            wrapper_inevitable.save(session, trigger_time, chat_data.last_triggered),
            wrapper_shuffled.save(session, trigger_time)
        )
        chat_data.last_given_titles_count = len(inevitable_titles) + len(shuffled_titles)
    chat_data.last_triggered = trigger_time
    session.commit()
    return records


TitleT = TypeVar("TitleT", bound=TitleFromGroupChat)


class NewTitles(Generic[TitleT]):
    def __init__(self, titles: List[TitleT], participants: List['Participant']):
        assert len(titles) == len(participants)
        self.titles: List[TitleT] = titles
        self.participants = participants


class NewInevitableTitles(NewTitles[InevitableTitle]):
    def save(
            self,
            session: Session,
            given_on: datetime,
            old_given_on: Optional[datetime]
    ) -> List[GivenInevitableTitle]:
        """Calculates new streak lengths and adds new given inevitable titles to database"""
        previous_streaks = self._load_old_streaks(session, old_given_on)
        records = []
        for participant, title in zip(self.participants, self.titles):
            new_streak_length = 1
            if previous_streaks:
                new_streak_length += previous_streaks.get(participant.id, 0)
            record = GivenInevitableTitle(
                participant=participant,
                title=title,
                given_on=given_on,
                streak_length=new_streak_length,
            )
            records.append(record)
            session.add(record)
        return records

    def _load_old_streaks(
            self, session: Session, old_given_on: Optional[datetime]
    ) -> Optional[Dict[int, int]]:
        if old_given_on is None:
            return None

        participant_filter = tuple_(
            GivenInevitableTitle.participant_id,
            GivenInevitableTitle.title_id
        ).in_(
            zip(self._get_participant_ids(), self._get_title_ids())
        )

        query = session.query(
            GivenInevitableTitle.participant_id,
            GivenInevitableTitle.streak_length
        ).filter(
            participant_filter,
            GivenInevitableTitle.given_on == old_given_on,
        )
        return dict(query)

    def _get_title_ids(self) -> Iterable[int]:
        return (i.id for i in self.titles)

    def _get_participant_ids(self) -> Iterable[int]:
        return (p.id for p in self.participants)


class NewShuffledTitles(NewTitles[ShuffledTitle]):
    def save(self, session: Session, given_on: datetime) -> List[GivenShuffledTitle]:
        """Adds new given shuffled titles to database"""
        records = []
        for participant, title in zip(self.participants, self.titles):
            record = GivenShuffledTitle(participant=participant, title=title, given_on=given_on)
            session.add(record)
            records.append(record)
        return records


def _choose_titles(
    chat: GroupChat,
) -> Optional[Tuple[List[InevitableTitle], List[ShuffledTitle], List[Participant]]]:
    participant_ids = chat.get_participant_ids()
    participant_count = len(participant_ids)
    if not participant_count:
        return None

    inevitable_titles: List[InevitableTitle] = chat.inevitable_titles[:participant_count]
    inevitable_titles_count = len(inevitable_titles)
    shuffled_titles_needed = min(
        participant_count - inevitable_titles_count,
        SHUFFLED_TITLES_TO_GIVE
    )
    shuffled_titles = chat.dequeue_shuffled_titles(shuffled_titles_needed)
    shuffled_titles_count = len(shuffled_titles)

    sample_size = shuffled_titles_count + inevitable_titles_count
    sample_items_inplace(participant_ids, sample_size)
    sampled_ids = participant_ids[:(-sample_size - 1):-1]
    participants = chat.get_participants_ordered(sampled_ids)

    return inevitable_titles, shuffled_titles, participants


def refresh_user_data(participants: List[Participant], tg_chat: Chat):
    """Gets current names and usernames of participants, updates database with this data and participation status"""
    if not participants:
        return

    for participant in participants:
        try:
            member = tg_chat.get_member(participant.user_id)
            user = member.user
            participant.full_name = user.full_name
            participant.username = user.username
            if member.status in (ChatMember.KICKED, ChatMember.LEFT):
                participant.is_active = False
        except error.BadRequest as ex:
            if ex.message == "User not found":
                participant.is_active = False
                participant.is_missing = True
