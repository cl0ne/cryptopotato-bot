import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import telegram
from sqlalchemy.orm import Session, joinedload
from telegram import Update, ParseMode, Chat, ChatAction, Bot
from telegram.ext import CallbackContext

from . import _strings as strings
from ._common import check_is_activity_enabled, PARTICIPATION_BUTTONS
from .assign_titles import assign_titles
from .group_migrated import try_migrate_chat_data
from .title_formatter import get_titles_text
from ...helpers import deletes_caller_message

if TYPE_CHECKING:
    from . import models

_logger = logging.getLogger(__name__)

COMMAND_DESCRIPTION = 'Show titles assigned today'
COOLDOWN_SECONDS = 60 * 2


@check_is_activity_enabled
@deletes_caller_message
def command_callback(update: Update, context: CallbackContext):
    """Announce current daily titles to the chat."""
    chat: Chat = update.effective_chat
    bot: Bot = context.bot
    bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
    from .models import GroupChat
    chat_data: GroupChat = context.daily_titles_group_chat
    now = datetime.now(timezone.utc)
    last_trigger_time = chat_data.last_triggered
    need_new_titles = (
            last_trigger_time is None
            or now.date() > last_trigger_time.date()
            or (not chat_data.last_given_titles_count
                and (now - last_trigger_time).seconds >= COOLDOWN_SECONDS)
    )
    session: Session = Session.object_session(chat_data)
    if need_new_titles:
        given_titles = assign_titles(session, chat_data, chat, now)
    else:
        from .models import GivenInevitableTitle, GivenShuffledTitle, Participant
        given_titles = (
            session.query(GivenInevitableTitle).options(
                joinedload(GivenInevitableTitle.participant)
            ).join(Participant).filter(
                GivenInevitableTitle.given_on == last_trigger_time,
                Participant.chat == chat_data
            ).all(),

            session.query(GivenShuffledTitle).options(
                joinedload(GivenShuffledTitle.participant)
            ).join(Participant).filter(
                GivenShuffledTitle.given_on == last_trigger_time,
                Participant.chat == chat_data
            ).all()
        )
    # TODO cache formatted titles
    title_texts = get_titles_text(*given_titles)
    send_titles_message(chat, chat_data, *title_texts)


def send_titles_message(chat: Chat, chat_data: 'models.GroupChat', titles_plain: str, titles: str):
    # To avoid excessive notifications for participants who got a title we initially send a message
    # with participant names in plain text and then edit sent message to add inline mentions to names
    do_edit = False
    if chat_data.last_given_titles_count is None:
        titles_text = strings.NO_PARTICIPANTS
    elif chat_data.last_given_titles_count == 0:
        titles_text = strings.NO_TITLES_IN_POOL
    else:
        titles_text = strings.MESSAGE__DAILY_TITLES.format(assigned_titles=titles_plain)
        do_edit = True
    send_message_kwargs = dict(parse_mode=ParseMode.MARKDOWN_V2, reply_markup=PARTICIPATION_BUTTONS)
    try:
        sent_message = chat.send_message(titles_text, **send_message_kwargs)
    except telegram.error.ChatMigrated as error:
        new_chat_id = error.new_chat_id
        _logger.info('Trying to migrate chat data for id %d to new id %d', chat.id, new_chat_id)
        session: Session = Session.object_session(chat_data)
        if not try_migrate_chat_data(session, chat_data, chat.id, new_chat_id):
            return
        _logger.info('Trying to resend message to %d', new_chat_id)
        sent_message = chat.bot.send_message(new_chat_id, titles_text, **send_message_kwargs)
    if do_edit:
        new_text = strings.MESSAGE__DAILY_TITLES.format(assigned_titles=titles)
        sent_message.edit_text(new_text, **send_message_kwargs)
