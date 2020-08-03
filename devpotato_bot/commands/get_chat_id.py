from telegram import Update, Chat, error, Message, ParseMode
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from devpotato_bot.helpers import try_delete_message

COMMAND_DESCRIPTION = 'Show current chat id'


def command_callback(update: Update, context: CallbackContext):
    """Show current chat id, use command argument 'hide' to receive it as a private message"""
    chat: Chat = update.effective_chat
    hide = False

    if chat.type == Chat.PRIVATE:
        message_text = f'id for this chat is equal to your id: `{chat.id}`'
    else:
        chat_title = escape_markdown(chat.title, version=2)
        message_text = f'id for {chat.type} "{chat_title}" is `{chat.id}`'
        hide = context.args and context.args[0].lower() == 'hide'
    user_id = update.effective_user.id
    message: Message = update.effective_message
    if not hide:
        message.reply_markdown_v2(message_text)
        return
    try_delete_message(message)
    try:
        context.bot.send_message(user_id, message_text, parse_mode=ParseMode.MARKDOWN_V2)
    except (error.Unauthorized, error.BadRequest):
        pass

