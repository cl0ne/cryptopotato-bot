from telegram import Update
from telegram.ext import CallbackContext

COMMAND_DESCRIPTION = 'Is potatobot online?'


def command_callback(update: Update, _context: CallbackContext):
    """Confirm bot's presence in the chat."""
    update.message.reply_text('Pong!')
