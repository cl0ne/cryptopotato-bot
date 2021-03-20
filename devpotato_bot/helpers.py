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
    admin_ids = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
    _logger.info(
        'Administrator ids requested for chat %d', chat_id
    )
    return admin_ids


class _AdminOnlyHandlerDecorator:
    def __init__(self, message_text):
        self.message_text = message_text

    def __call__(self, func):
        @wraps(func)
        def wrapper(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            chat: Chat = update.effective_chat
            message: Message = update.effective_message
            is_private_chat = chat.type == Chat.PRIVATE
            # sent by anonymous group chat admin or in a channel post
            is_requested_by_chat = chat == message.sender_chat
            is_denied = not(
                is_private_chat
                or is_requested_by_chat
                or user_id in get_admin_ids(context.bot, chat.id)
            )
            if is_denied:
                _logger.info(
                    'User %d from chat %d denied from using an admin-only command: %s',
                    user_id, chat.id, func.__module__
                )
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
