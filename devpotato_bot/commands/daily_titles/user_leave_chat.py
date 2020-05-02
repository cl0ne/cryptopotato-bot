from sqlalchemy.orm import Session
from telegram import Update, Chat, Message, User
from telegram.ext import CallbackContext

from devpotato_bot.commands.daily_titles._scoped_session import scoped_session


def message_callback(update: Update, context: CallbackContext):
    """Handle users leaving the chat."""
    with scoped_session(context.session_factory) as session:  # type: Session
        chat: Chat = update.effective_chat
        from .models import GroupChat
        chat_data: GroupChat = GroupChat.get_by_id(session, chat.id)
        if chat_data is None:
            return
        message: Message = update.effective_message
        user_gone: User = message.left_chat_member
        participant = chat_data.get_participant(user_gone.id)
        if participant is None or not participant.is_active:
            return
        participant.full_name = user_gone.full_name
        participant.username = user_gone.username
        participant.is_active = False
        session.commit()
