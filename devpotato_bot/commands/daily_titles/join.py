from typing import TYPE_CHECKING

from sqlalchemy.orm import Session
from telegram import Update, User, ParseMode, Chat, CallbackQuery
from telegram.ext import CallbackContext

from . import _strings as strings
from ._common import check_is_activity_enabled
from ._scoped_session import scoped_session
from ...helpers import deletes_caller_message

if TYPE_CHECKING:
    from . import models

COMMAND_DESCRIPTION = 'Begin participation in Daily Titles assignment'


@check_is_activity_enabled
@deletes_caller_message
def command_callback(update: Update, context: CallbackContext):
    """Join daily titles assignment in the chat via command."""
    user: User = update.effective_user
    state_changed = _participation_join(user, context.daily_titles_group_chat)
    if state_changed:
        reply_text = strings.MESSAGE__JOINED
    else:
        reply_text = strings.MESSAGE__ALREADY_JOINED
    reply_text.format(mention=user.mention_html())
    update.effective_chat.send_message(reply_text, parse_mode=ParseMode.HTML)


def button_callback(update: Update, context: CallbackContext):
    """Join to daily titles assignment in the chat via button."""
    query: CallbackQuery = update.callback_query
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    with scoped_session(context.session_factory) as session:  # type: Session
        from .models import GroupChat
        chat_data = GroupChat.get_by_id(session, chat.id)
        is_enabled_here = chat_data is not None and chat_data.is_enabled
        if is_enabled_here:
            state_changed = _participation_join(user, chat_data)
    if not is_enabled_here:
        reply_text = strings.POPUP__NOT_ENABLED
    elif state_changed:
        reply_text = strings.POPUP__JOINED
    else:
        reply_text = strings.POPUP__ALREADY_JOINED
    query.answer(text=reply_text)


def _participation_join(user: User, chat_data: 'models.GroupChat') -> bool:
    """Add user to daily titles assignment participants of the chat"""
    session: Session = Session.object_session(chat_data)
    participant = chat_data.get_participant(user.id)
    state_changed = True
    if participant is None:
        from .models import Participant
        participant = Participant(user_id=user.id, chat=chat_data, is_active=True)
        session.add(participant)
    elif participant.is_active:
        state_changed = False
    else:
        participant.is_active = True
    participant.full_name = user.full_name
    participant.username = user.username
    session.commit()
    return state_changed
