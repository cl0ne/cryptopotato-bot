from sqlalchemy.orm import Session
from telegram import Update, ParseMode, Chat
from telegram.ext import CallbackContext

from . import _strings as strings
from ._common import PARTICIPATION_BUTTONS
from ._scoped_session import scoped_session
from .models import GroupChat
from ...helpers import admin_only, deletes_caller_message

COMMAND_DESCRIPTION = 'Enable Daily Titles Assignment for this chat'


@admin_only(strings.MESSAGE__ENABLE_REQUIRES_ADMIN)
@deletes_caller_message
def command_callback(update: Update, context: CallbackContext):
    """Enable daily titles assignment in the chat."""
    chat: Chat = update.effective_chat
    with scoped_session(context.session_factory) as session:  # type: Session
        chat_data: GroupChat = GroupChat.get_by_id(session, chat.id)
        reply_html = strings.MESSAGE__ENABLED
        if chat_data is None:
            chat_data = GroupChat(chat_id=chat.id, is_enabled=True)
            session.add(chat_data)
        elif chat_data.is_enabled:
            reply_html = strings.MESSAGE__ALREADY_ENABLED
        else:
            chat_data.is_enabled = True
        chat_data.name = chat.title
        session.commit()
    chat.send_message(reply_html, parse_mode=ParseMode.HTML, reply_markup=PARTICIPATION_BUTTONS)
