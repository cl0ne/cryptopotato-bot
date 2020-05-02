from sqlalchemy.orm import Session
from telegram import Update, ParseMode, Chat
from telegram.ext import CallbackContext

from . import _strings as strings
from ._scoped_session import scoped_session
from .models import GroupChat
from ...helpers import admin_only, deletes_caller_message


@admin_only(strings.MESSAGE__DISABLE_REQUIRES_ADMIN)
@deletes_caller_message
def command_callback(update: Update, context: CallbackContext):
    """Enable daily titles assignment in the chat."""
    chat: Chat = update.effective_chat
    with scoped_session(context.session_factory) as session:  # type: Session
        chat_data: GroupChat = GroupChat.get_by_id(session, chat.id)
        reply_html = strings.MESSAGE__ALREADY_DISABLED
        if chat_data is None:
            chat_data = GroupChat(chat_id=chat.id, is_enabled=False)
            session.add(chat_data)
            reply_html = strings.MESSAGE__WAS_NEVER_ENABLED
        elif chat_data.is_enabled:
            chat_data.is_enabled = False
            reply_html = strings.MESSAGE__DISABLED
        chat_data.name = chat.title
        session.commit()

    chat.send_message(reply_html, parse_mode=ParseMode.HTML)
