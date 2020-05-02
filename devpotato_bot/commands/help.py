from telegram import Update
from telegram.ext import CallbackContext

from . import roll


def command_callback(update: Update, _context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_markdown_v2(
        '*Available commands:*\n\n'

        '/me \\- announce your actions to the chat\n'
        '\n'
        '/ping \\- check if bot is currently active\n'
        '\n'
        f'/roll or /r \\- make a dice roll in {roll.NOTATION_DESCRIPTION}\n'
        '\n'
        '/fortune \\- get a random epigram\n'
        '\n'
        '/daily\\_titles \\- Show titles assigned today'
        '\n'
        '/daily\\_titles\\_join \\- Begin participation in Daily Titles Assignment\n'
        '/daily\\_titles\\_leave \\- Cease participation in Daily Titles Assignment\n'
        '/daily\\_titles\\_start \\- Enable Daily Titles Assignment for chat\n'
        '/daily\\_titles\\_stop \\- Stop Daily Titles Assignment for chat\n'
        '\n'
        '/titles\\_pool \\- Edit titles available for assignment\n'
        '\n'
        '/get\\_chat\\_id \\- Show current chat id',
        disable_web_page_preview=True
    )
