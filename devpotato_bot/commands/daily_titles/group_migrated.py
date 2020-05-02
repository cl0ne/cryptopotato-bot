import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from telegram import Update, Chat, Message
from telegram.ext import CallbackContext

from devpotato_bot.commands.daily_titles._scoped_session import scoped_session

_logger = logging.getLogger(__name__)


def try_migrate_chat_data(session, chat_data, old_chat_id, new_chat_id):
    chat_data.chat_id = new_chat_id
    try:
        session.commit()
        _logger.info('Successfully migrated to chat data id from %d to %d', old_chat_id, new_chat_id)
        return True
    except IntegrityError:  # this shouldn't happen though
        _logger.info('Conflict during migration of chat dta id from %d to %d', old_chat_id, new_chat_id)
        session.rollback()
        chat_data.is_migration_conflicted = True
        chat_data.is_enabled = False
        session.commit()
        return False


def message_callback(update: Update, context: CallbackContext):
    """Handle group to supergroup migration."""
    with scoped_session(context.session_factory) as session:  # type: Session
        message: Message = update.effective_message
        old_chat_id = message.migrate_from_chat_id
        from .models import GroupChat
        chat_data: GroupChat = GroupChat.get_by_id(session, old_chat_id)
        if chat_data is None:
            return
        new_chat_id = message.migrate_to_chat_id
        try_migrate_chat_data(session, chat_data, old_chat_id, new_chat_id)
