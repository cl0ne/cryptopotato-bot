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

COMMAND_DESCRIPTION = 'Cease participation in Daily Titles assignment'


@check_is_activity_enabled
@deletes_caller_message
def command_callback(update: Update, context: CallbackContext):
    """Cease to participate in daily titles assignment in the chat via command."""
    user: User = update.effective_user
    state_changed = _participation_leave(user, context.daily_titles_group_chat)
    if state_changed:
        reply_text = strings.MESSAGE__LEFT
    else:
        reply_text = strings.MESSAGE__NOT_PARTICIPATING
    reply_text.format(mention=user.mention_html())
    update.effective_chat.send_message(reply_text, parse_mode=ParseMode.HTML)


def button_callback(update: Update, context: CallbackContext):
    """Cease to participate in daily titles assignment in the chat via button."""
    query: CallbackQuery = update.callback_query
    user: User = update.effective_user
    chat: Chat = update.effective_chat
    with scoped_session(context.session_factory) as session:  # type: Session
        from .models import GroupChat
        chat_data = GroupChat.get_by_id(session, chat.id)
        is_enabled_here = chat_data is not None and chat_data.is_enabled
        if is_enabled_here:
            state_changed = _participation_leave(user, chat_data)
    if not is_enabled_here:
        reply_text = strings.POPUP__NOT_ENABLED
    elif state_changed:
        reply_text = strings.POPUP__LEFT
    else:
        reply_text = strings.POPUP__NOT_PARTICIPATING
    query.answer(text=reply_text)


def _participation_leave(user: User, chat_data: 'models.GroupChat') -> bool:
    """Remove user from daily titles assignment participants of the chat"""
    participant: models.Participant = chat_data.get_participant(user.id)
    state_changed = participant is not None and participant.is_active
    if state_changed:
        participant.full_name = user.full_name
        participant.username = user.username
        participant.is_active = False
        Session.object_session(chat_data).commit()
    return state_changed
