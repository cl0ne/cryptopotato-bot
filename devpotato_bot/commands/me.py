from telegram import Update, Message, Chat, ParseMode
from telegram.ext import CallbackContext

from ..helpers import deletes_caller_message


@deletes_caller_message
def _me_callback(update: Update, context: CallbackContext):
    """Announce sender's actions to the chat."""
    message: Message = update.message
    status = message.text_html.split(None, 1)[1:]
    status = status[0] if status else 'completely failed to describe his own actions'
    name = '<b>***</b>{}'.format(update.effective_user.mention_html())
    text = '{} {}'.format(name, status)
    chat: Chat = update.effective_chat
    context.bot.send_message(chat.id, text, disable_web_page_preview=True, parse_mode=ParseMode.HTML)


def get_handler(**kwargs):
    from telegram.ext import Filters, CommandHandler
    return CommandHandler("me", _me_callback, filters=~Filters.update.edited_message)