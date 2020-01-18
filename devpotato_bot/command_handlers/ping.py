from telegram import Update
from telegram.ext import CallbackContext


def _ping_callback(update: Update, context: CallbackContext):
    """Confirm bot's presence in the chat."""
    update.message.reply_text('Pong!')


def get_handler(**kwargs):
    from telegram.ext import Filters, CommandHandler
    return CommandHandler("ping", _ping_callback, filters=~Filters.update.edited_message)
