from __future__ import annotations

from typing import TYPE_CHECKING

from telegram.utils.helpers import escape_markdown, mention_markdown

from ._strings import STREAK_MARK

if TYPE_CHECKING:
    from .models import GivenShuffledTitle
    from .models import GivenInevitableTitle
    from typing import List, Tuple


def format_given_shuffled_title(record: 'GivenShuffledTitle'):
    participant = record.participant
    user_name = escape_markdown(participant.full_name, version=2)
    title_text = escape_markdown(record.title.text, version=2)
    mention = mention_markdown(participant.user_id, participant.full_name, version=2)
    plain = f" {user_name} \\- {title_text}"
    with_mention = f" {mention} \\- {title_text}"
    return plain, with_mention


def _format_streak_mark(streak_length: int):
    if streak_length < 2:
        return ""
    return f"{streak_length}x{STREAK_MARK} "


def format_given_inevitable_title(record: 'GivenInevitableTitle'):
    participant = record.participant
    user_name = escape_markdown(participant.full_name, version=2)
    title_text = escape_markdown(record.title.text, version=2)
    streak_mark = _format_streak_mark(record.streak_length)
    mention = mention_markdown(participant.user_id, participant.full_name, version=2)
    plain = f" {streak_mark}{user_name} \\- {title_text}"
    with_mention = f" {streak_mark}{mention} \\- {title_text}"
    return plain, with_mention


def _format_lines(records, formatter, lines_plain, lines_mention):
    for plain, mention in map(formatter, records):
        lines_plain.append(plain)
        lines_mention.append(mention)


def get_titles_text(
        inevitable_titles: List['GivenInevitableTitle'],
        shuffled_titles: List['GivenShuffledTitle']
) -> Tuple[str, str]:
    if not (inevitable_titles or shuffled_titles):
        return '', ''

    lines_plain, lines_mention = [], []  # type: List[str], List[str]

    _format_lines(inevitable_titles, format_given_inevitable_title, lines_plain, lines_mention)

    if inevitable_titles and shuffled_titles:
        lines_plain.append("")
        lines_mention.append("")

    _format_lines(shuffled_titles, format_given_shuffled_title, lines_plain, lines_mention)

    return "\n".join(lines_plain), "\n".join(lines_mention)
