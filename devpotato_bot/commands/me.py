from telegram import Update, Message, Chat, ParseMode
from telegram.ext import CallbackContext

from ..helpers import deletes_caller_message

COMMAND_DESCRIPTION = 'Announce your actions to the chat'


@deletes_caller_message
def command_callback(update: Update, context: CallbackContext):
    """Announce sender's actions to the chat."""
    message: Message = update.message
    status = message.text_html.split(None, 1)[1:]
    status = status[0] if status else 'completely failed to describe his own actions'
    name = '<b>***{}</b>'.format(update.effective_user.mention_html())
    text = '{} {}'.format(name, status)
    chat: Chat = update.effective_chat
    message_kwargs = dict(chat_id=chat.id, text=text, parse_mode=ParseMode.HTML)
    reply_to = message.reply_to_message
    if reply_to is not None:
        message_kwargs['reply_to_message_id'] = reply_to.message_id
    context.bot.send_message(**message_kwargs)
