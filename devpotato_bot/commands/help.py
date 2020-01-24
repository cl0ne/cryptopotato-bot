from telegram import Update
from telegram.ext import CallbackContext

from . import roll


def _help_callback(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_markdown(
        '*Available commands:*\n\n'

        '*/me* - announce your actions to the chat\n'
        '\n'
        '*/ping* - check if bot is currently active\n'
        '\n'
        f'*/roll* or */r* - make a dice roll in {roll.NOTATION_DESCRIPTION}\n'
        '\n'
        '*/fortune* - get a random epigram',
        disable_web_page_preview=True
    )


def get_handler(**kwargs):
    from telegram.ext import CommandHandler
    return CommandHandler("help", _help_callback)
