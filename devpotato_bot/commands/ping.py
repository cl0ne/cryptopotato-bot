from telegram import Update
from telegram.ext import CallbackContext


def command_callback(update: Update, _context: CallbackContext):
    """Confirm bot's presence in the chat."""
    update.message.reply_text('Pong!')
