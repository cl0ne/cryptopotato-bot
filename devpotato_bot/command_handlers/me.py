from telegram import Update, Message
from telegram.ext import CallbackContext


def _me_callback(update: Update, context: CallbackContext):
    """Announce sender's actions to the chat."""
    message: Message = update.message
    status = message.text_html.split(None, 1)[1:]
    status = status[0] if status else 'completely failed to describe his own actions'
    name = '<b>***</b>{}'.format(update.effective_user.mention_html())
    text = '{} {}'.format(name, status)
    message.reply_html(text, quote=False, disable_web_page_preview=True)
    context.bot.delete_message(message.chat_id, message.message_id)


def get_handler(**kwargs):
    from telegram.ext import Filters, CommandHandler
    return CommandHandler("me", _me_callback, filters=~Filters.update.edited_message)
