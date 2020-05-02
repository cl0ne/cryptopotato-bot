import logging
from functools import wraps
from typing import Callable

import telegram.error
from cachetools import cached, TTLCache
from telegram import Chat, Update, Message
from telegram.ext import CallbackContext

_logger = logging.getLogger(__name__)


@cached(cache=TTLCache(maxsize=256, ttl=60*60))
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


class _AdminOnlyHandlerDecorator:
    def __init__(self, message_text):
        self.message_text = message_text

    def __call__(self, func):
        @wraps(func)
        def wrapper(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            chat: Chat = update.effective_chat
            message: Message = update.effective_message
            if chat.type != Chat.PRIVATE and user_id not in get_admin_ids(context.bot, message.chat_id):
                message.reply_text(self.message_text)
                return
            return func(update, context)
        return wrapper


admin_only = _AdminOnlyHandlerDecorator     # silence style checker


def developer_only(func: Callable):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        if user_id not in context.developer_ids:
            return  # ignore everyone else
        return func(update, context)
    return wrapper


def try_delete_message(message: Message):
    try:
        return message.delete()
    except telegram.error.BadRequest:
        # deletion failed most likely due to lack of permissions in the chat
        # we can safely ignore it
        return False


def deletes_caller_message(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        try_delete_message(update.effective_message)
        return func(update, context)
    return wrapper
