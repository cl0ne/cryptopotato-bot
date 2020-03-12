import logging
from functools import wraps

import telegram.error
from telegram import Update, Message, Bot
from telegram.ext import CallbackContext
from typing import Set

_logger = logging.getLogger(__name__)


class _DeveloperOnlyHandlerDecorator:
    def __init__(self, developer_ids: Set[int]):
        self.developer_ids = developer_ids

    def __call__(self, func):
        @wraps(func)
        def wrapper(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            if user_id not in self.developer_ids:
                return  # ignore everyone else
            return func(update, context)
        return wrapper


developer_only = _DeveloperOnlyHandlerDecorator     # silence style checker


def deletes_caller_message(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        bot: Bot = context.bot
        message: Message = update.effective_message
        try:
            bot.delete_message(message.chat_id, message.message_id)
        except telegram.error.BadRequest:
            # deletion failed most likely due to lack of permissions in the chat
            # we can safely ignore it most of the time
            pass
        return func(update, context)
    return wrapper
