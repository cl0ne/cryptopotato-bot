import logging

from sqlalchemy.orm import Session
from telegram import Bot, User, ChatMember, error
from telegram import Update, Chat
from telegram.ext import CallbackContext

from ._scoped_session import scoped_session
from devpotato_bot.helpers import developer_only

_logger = logging.getLogger(__name__)
_disable_activity_if_kicked_message = 'Looks like the bot was kicked from chat with id %d, disable activity'


@developer_only
def command_callback(update: Update, context: CallbackContext):
    """Refresh daily titles participation status"""

    bot: Bot = context.bot
    from .models import GroupChat, Participant
    user: User = update.effective_user
    _logger.info('User %d requested refreshing daily titles participants', user.id)

    disabled_chats = 0
    inactive_users = 0
    missing_users = 0
    errors = 0

    with scoped_session(context.session_factory) as session:  # type: Session
        chat_data: GroupChat
        for chat_data in session.query(GroupChat).filter(GroupChat.is_enabled).all():
            tg_chat = None
            try:
                tg_chat = bot.get_chat(chat_data.chat_id)
                if tg_chat.type == Chat.PRIVATE:
                    # Should never happen though
                    _logger.warning('Skip private chat with id %d, disable activity', tg_chat.id)
                    chat_data.is_enabled = False
                    session.commit()
                    disabled_chats += 1
                    continue

                participants_new_data = []
                q = session.query(Participant.user_id, Participant.id)
                q = q.filter(Participant.is_active, Participant.chat == chat_data)
                for user_id, participant_id in q.all():
                    new_user_data = dict(id=participant_id)
                    try:
                        member: ChatMember = tg_chat.get_member(user_id)
                    except error.BadRequest as e:
                        if e.message != 'User not found':
                            error_message = 'Failed to get participant with id %d for chat with id %d: %s'
                            _logger.error(error_message, participant_id, chat_data.chat_id, e.message)
                            errors += 1
                            continue
                        new_user_data.update(is_active=False, is_missing=True)
                        missing_users += 1
                    else:
                        u = member.user
                        new_user_data.update(full_name=u.full_name, username=u.username)
                        if member.status in (ChatMember.KICKED, ChatMember.LEFT):
                            new_user_data.update(is_active=False)
                            inactive_users += 1
                    participants_new_data.append(new_user_data)
                session.bulk_update_mappings(Participant, participants_new_data)
                session.commit()
            except error.Unauthorized as e:
                _logger.info(
                    _disable_activity_if_kicked_message,
                    chat_data.chat_id,
                    exc_info=e
                )
                chat_data.is_enabled = False
                session.commit()
                disabled_chats += 1
            except error.TelegramError as e:
                if tg_chat is None:
                    error_message = 'Failed to get a chat with id %d'
                else:
                    error_message = 'Getting participants from chat with id %d failed'
                _logger.error(error_message, chat_data.chat_id, exc_info=e)
                errors += 1

    _logger.info('Daily titles participants refresh completed')

    message_text = (
        'Daily titles participants refresh completed:\n'
        '\n'
        f' deactivated {disabled_chats} chats\n'
        f' deactivated {inactive_users} participants\n'
        f' {missing_users} participants flagged as missing\n'
        f' {errors} errors occurred'
    )
    update.effective_message.reply_text(message_text)
