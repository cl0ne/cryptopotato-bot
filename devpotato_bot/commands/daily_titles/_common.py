from functools import wraps

from sqlalchemy.orm import Session
from telegram import Update, Chat, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from . import _strings as strings
from ._scoped_session import scoped_session
from ... import base_handlers


PARTICIPATION_BUTTONS = InlineKeyboardMarkup.from_row([
    InlineKeyboardButton("✖️ leave", callback_data='daily_titles.leave'),
    InlineKeyboardButton("✊ join", callback_data='daily_titles.join')
])


def check_is_activity_enabled(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        chat: Chat = update.effective_chat
        with scoped_session(context.session_factory) as session:  # type: Session
            from .models import GroupChat
            chat_data = GroupChat.get_by_id(session, chat.id)
            is_enabled_here = chat_data is not None and chat_data.is_enabled
            if is_enabled_here:
                context.daily_titles_group_chat = chat_data
                return func(update, context)
        update.effective_message.reply_html(strings.MESSAGE__NOT_ENABLED)
    return wrapper


class CommandHandler(base_handlers.CommandHandler):
    def handle_update(self, update: Update, dispatcher, check_result, context=None):
        chat: Chat = update.effective_chat
        if chat.type == Chat.PRIVATE:
            chat.send_message(
                strings.MESSAGE__DISABLED_FOR_PRIVATE_CHATS,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        return super().handle_update(update, dispatcher, check_result, context)
