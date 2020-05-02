import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import telegram
from sqlalchemy.orm import Session
from telegram import Update, ParseMode, Chat, ChatAction, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from . import _strings as strings
from ._common import check_is_activity_enabled, PARTICIPATION_BUTTONS
from .assign_titles import assign_titles
from .group_migrated import try_migrate_chat_data
from ...helpers import deletes_caller_message

if TYPE_CHECKING:
    from . import models

_logger = logging.getLogger(__name__)


@check_is_activity_enabled
@deletes_caller_message
def command_callback(update: Update, context: CallbackContext):
    """Announce current daily titles to the chat."""
    chat: Chat = update.effective_chat
    bot: Bot = context.bot
    bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
    from .models import GroupChat
    chat_data: GroupChat = context.daily_titles_group_chat
    if chat_data.copy_default_titles:
        chat_data.do_copy_default_titles()
    now = datetime.now(timezone.utc)
    need_new_titles = (
            chat_data.last_triggered is None
            or now.date() > chat_data.last_triggered.date()
            or (chat_data.last_titles is None
                and (now - chat_data.last_triggered).seconds >= 60 * 2)
    )
    if need_new_titles:
        session: Session = Session.object_session(chat_data)
        assign_titles(session, chat_data, chat, now)
    send_titles_message(chat, chat_data)


def send_titles_message(chat: Chat, chat_data: 'models.GroupChat'):
    do_edit = False
    if chat_data.last_titles is None:
        titles_text = strings.NO_PARTICIPANTS
    else:
        titles_text = strings.MESSAGE__DAILY_TITLES.format(assigned_titles=chat_data.last_titles_plain)
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
        new_text = strings.MESSAGE__DAILY_TITLES.format(assigned_titles=chat_data.last_titles)
        sent_message.edit_text(new_text, **send_message_kwargs)
