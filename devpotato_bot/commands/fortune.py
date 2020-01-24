import logging
import subprocess

from telegram import Update, Message, ChatAction, Bot, ParseMode
from telegram.ext import CallbackContext, run_async

_logger = logging.getLogger(__name__)


@run_async
def _fortune_callback(update: Update, context: CallbackContext):
    """Get random epigram from `fortune`."""
    message: Message = update.effective_message
    bot: Bot = context.bot
    bot.send_chat_action(chat_id=message.chat_id, action=ChatAction.TYPING)
    try:
        result = subprocess.run(['fortune', '-a'], capture_output=True, text=True, timeout=2)
        context.bot.delete_message(message.chat_id, message.message_id)
        user_name = update.effective_user.mention_html()
        reply_text = (
            f'<b>Fortune</b> for {user_name}:\n'
            '\n'
            f'{result.stdout}'
        )
        bot.send_message(message.chat_id, reply_text, parse_mode=ParseMode.HTML)
    except (OSError, TimeoutError) as error:
        _logger.warning('Failed to call fortune executable: %s', error)


def get_handler(**kwargs):
    from telegram.ext import Filters, CommandHandler
    return CommandHandler("fortune", _fortune_callback, filters=~Filters.update.edited_message)
