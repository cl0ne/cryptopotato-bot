import logging
from datetime import datetime, timezone
from typing import List

import telegram.error
from telegram import Chat, Bot, TelegramError
from telegram.ext import CallbackContext, Job

from .show import send_titles_message

_logger = logging.getLogger(__name__)
_disable_activity_if_kicked_message = 'Looks like the bot was kicked from chat with id %d, disable activity'


def job_callback(context: CallbackContext):
    _logger.info('Starting daily titles assignment job')
    job: Job = context.job
    bot: Bot = context.bot
    from sqlalchemy.orm import Session
    session: Session = job.context()

    from .models import GroupChat, Participant
    chat_query = session.query(GroupChat).filter(GroupChat.is_enabled)
    chat_query = chat_query.filter(GroupChat.participants.any(Participant.is_active))
    chats: List[GroupChat] = chat_query.all()

    _logger.info('Enqueued %d chat(s)', len(chats))

    now = datetime.now(timezone.utc)
    for c in chats:
        if c.last_triggered is not None and now.date() <= c.last_triggered.date():
            _logger.info('Skip chat with id %d: already assigned', c.chat_id)
            continue
        try:
            tg_chat: Chat = bot.get_chat(c.chat_id)
        except telegram.error.Unauthorized as e:
            _logger.info(
                _disable_activity_if_kicked_message,
                c.chat_id,
                exc_info=e
            )
            c.is_enabled = False
            session.commit()
            continue
        except TelegramError as error:
            _logger.error('Failed to get a chat with id %d', c.chat_id, exc_info=error)
            continue

        if tg_chat.type == Chat.PRIVATE:
            # Should never happen though
            _logger.warning('Skip private chat with id %d, disable activity', tg_chat.id)
            c.is_enabled = False
            session.commit()
            continue

        from .assign_titles import assign_titles
        assign_titles(session, c, tg_chat, now)
        try:
            send_titles_message(tg_chat, c)
        except telegram.error.Unauthorized as e:
            _logger.info(
                _disable_activity_if_kicked_message,
                tg_chat.id,
                exc_info=e
            )
            c.is_enabled = False
            session.commit()
        except TelegramError as error:
            _logger.error('Sending to chat with id %d failed', tg_chat.id, exc_info=error)
    session.close()
    _logger.info('Daily titles assignment job: done')
