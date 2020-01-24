from functools import wraps

import telegram.error
from telegram import Update, Message, Bot
from telegram.ext import CallbackContext


def deletes_caller_message(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        bot: Bot = context.bot
        message: Message = update.effective_message
        try:
            bot.delete_message(message.chat_id, message.message_id)
        except telegram.error.BadRequest:
            pass
        return func(update, context)
    return wrapper
