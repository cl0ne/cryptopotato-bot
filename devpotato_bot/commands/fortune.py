import logging
import subprocess

from telegram import Update, ChatAction, Bot, ParseMode, Chat
from telegram.ext import CallbackContext

from ..helpers import deletes_caller_message

_logger = logging.getLogger(__name__)


COMMAND_DESCRIPTION = 'Get yourself a random epigram'


@deletes_caller_message
def command_callback(update: Update, context: CallbackContext):
    """Get random epigram from `fortune`."""
    bot: Bot = context.bot
    chat: Chat = update.effective_chat
    bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
    user_name = update.effective_user.mention_html()
    try:
        result = subprocess.run(['fortune', '-a'], capture_output=True, text=True, timeout=2)
        reply_text = (
            f'<b>Fortune</b> for {user_name}:\n'
            '\n'
            f'{result.stdout}'
        )
    except (OSError, TimeoutError) as error:
        _logger.warning('Failed to call fortune executable', exc_info=error)
        reply_text = fr'Not enough entropy to tell <b>Fortune</b> for {user_name} 🤷‍¯\_(ツ)_/¯️'
    bot.send_message(chat.id, reply_text, parse_mode=ParseMode.HTML)
