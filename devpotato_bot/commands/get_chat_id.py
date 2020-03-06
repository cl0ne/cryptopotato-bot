from telegram import Update, Chat
from telegram.ext import CallbackContext

from devpotato_bot.helpers import deletes_caller_message, developer_only


def _build_callback(developer_ids):
    @deletes_caller_message
    @developer_only(developer_ids)
    def _callback(update: Update, context: CallbackContext):
        """Send chat id to developer's private messages"""
        chat: Chat = update.effective_chat
        if chat.type == Chat.PRIVATE:
            return
        message_text = f'id for {chat.type} "{chat.title}" is {chat.id}'
        user_id = update.effective_user.id
        context.bot.send_message(user_id, message_text)
    return _callback


def get_handler(*, developer_ids, **kwargs):
    from telegram.ext import Filters, CommandHandler
    return CommandHandler(
        "get_chat_id",
        _build_callback(developer_ids),
        filters=~Filters.update.edited_message
    )
