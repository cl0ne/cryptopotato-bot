from telegram import Update, Chat, error, Message
from telegram.ext import CallbackContext

from devpotato_bot.helpers import try_delete_message


def command_callback(update: Update, context: CallbackContext):
    """Show current chat id, use command argument 'hide' to receive it as a private message"""
    chat: Chat = update.effective_chat
    hide = False

    if chat.type == Chat.PRIVATE:
        message_text = f'id for this chat is equal to your id: {chat.id}'
    else:
        message_text = f'id for {chat.type} "{chat.title}" is {chat.id}'
        hide = context.args and context.args[0].lower() == 'hide'
    user_id = update.effective_user.id
    message: Message = update.effective_message
    if not hide:
        message.reply_text(message_text)
        return
    try_delete_message(message)
    try:
        context.bot.send_message(user_id, message_text)
    except (error.Unauthorized, error.BadRequest):
        pass

