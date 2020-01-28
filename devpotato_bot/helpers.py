import logging
from functools import wraps

import telegram.error
from telegram import Update, Message, Bot
from telegram.ext import CallbackContext

_logger = logging.getLogger(__name__)


def deletes_caller_message(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        bot: Bot = context.bot
        message: Message = update.effective_message
        try:
            bot.delete_message(message.chat_id, message.message_id)
        except telegram.error.BadRequest as e:
            _logger.warning('Message with id %d was not deleted', exc_info=e)
        return func(update, context)
    return wrapper
