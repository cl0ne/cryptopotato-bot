import itertools
from typing import List, Tuple, Union

from sqlalchemy.orm import Session
from telegram import Chat, User, error, ChatMember
from telegram.utils.helpers import escape_markdown, mention_markdown

from .models import GroupChat, InevitableTitle, ShuffledTitle
from ...sample import sample_items_inplace

SHUFFLED_TITLES_TO_GIVE = 5


class MissingUserWrapper:
    def __init__(self, user_id):
        self.user_id = user_id
        self.full_name = ''

    def mention_markdown_v2(self):
        return mention_markdown(self.user_id, self.full_name, version=2)


def _get_titles_assignment(chat: GroupChat):
    participant_ids = chat.get_participant_ids()
    participant_count = len(participant_ids)
    if not participant_count:
        return None

    inevitable_titles: List[InevitableTitle] = chat.inevitable_titles[:participant_count]
    inevitable_titles_count = len(inevitable_titles)
    if inevitable_titles_count:
        sample_items_inplace(participant_ids, inevitable_titles_count)

    shuffled_titles_needed = min(participant_count - inevitable_titles_count, SHUFFLED_TITLES_TO_GIVE)
    shuffled_titles = chat.dequeue_shuffled_titles(shuffled_titles_needed)
    shuffled_titles_count = len(shuffled_titles)
    if shuffled_titles_count:
        item_limit = participant_count - inevitable_titles_count
        sample_items_inplace(participant_ids, shuffled_titles_count, item_limit=item_limit)
    sampled_count = shuffled_titles_count + inevitable_titles_count
    sampled_ids = list(itertools.islice(reversed(participant_ids), sampled_count))
    return sampled_ids, inevitable_titles, shuffled_titles


def _get_assigned_users(tg_chat: Chat, chat: GroupChat, user_ids):
    users = []
    participants_new_data, load_from_db = [], {}
    for participant_id, user_id in user_ids:
        new_user_data = dict(id=participant_id)
        try:
            member = tg_chat.get_member(user_id)
            u = member.user
            new_user_data.update(full_name=u.full_name, username=u.username)
            if member.status in (ChatMember.KICKED, ChatMember.LEFT):
                new_user_data.update(is_active=False)
            participants_new_data.append(new_user_data)
        except error.BadRequest as e:
            if e.message == 'User not found':
                new_user_data.update(is_active=False, is_missing=True)
                participants_new_data.append(new_user_data)
            u = MissingUserWrapper(user_id)
            load_from_db[participant_id] = u
        users.append(u)
    session: Session = Session.object_session(chat)
    from .models import Participant
    session.bulk_update_mappings(Participant, participants_new_data)
    session.commit()
    loaded_names = session.query(
        Participant.id, Participant.full_name
    ).filter(Participant.id.in_(load_from_db)).all()
    for participant_id, participant_name in loaded_names:
        load_from_db[participant_id].full_name = participant_name
    return users


def _format_assignment_lines(participants, titles, lines_plain, lines_mention):
    for user, title in zip(participants, titles):
        user_name = escape_markdown(user.full_name, version=2)
        title_text = escape_markdown(title.text, version=2)
        lines_plain.append(f' {user_name} \\- {title_text}')
        lines_mention.append(f' {user.mention_markdown_v2()} \\- {title_text}')


def _build_titles_text(
        participants: List[Union[User, MissingUserWrapper]],
        inevitable_titles: List[InevitableTitle],
        shuffled_titles: List[ShuffledTitle]
) -> Tuple[str, str]:
    lines_mention, lines_plain = [], []
    _format_assignment_lines(participants, inevitable_titles, lines_plain, lines_mention)

    if inevitable_titles and shuffled_titles:
        lines_plain.append('')
        lines_mention.append('')

    inevitable_titles_count = len(inevitable_titles)
    participants_for_shuffled = itertools.islice(participants, inevitable_titles_count, None)
    _format_assignment_lines(participants_for_shuffled, shuffled_titles, lines_plain, lines_mention)

    return '\n'.join(lines_plain), '\n'.join(lines_mention)


def assign_titles(session, chat_data, tg_chat, trigger_time):
    assignment = _get_titles_assignment(chat_data)
    new_titles = None, None
    if assignment is not None:
        participant_ids, *titles = assignment
        users = _get_assigned_users(tg_chat, chat_data, participant_ids)
        new_titles = _build_titles_text(users, *titles)
    chat_data.last_titles_plain, chat_data.last_titles = new_titles
    chat_data.last_triggered = trigger_time
    chat_data.name = tg_chat.title
    session.commit()
