import itertools
from typing import Optional, List

from sqlalchemy.orm import Session
from telegram import Update, Message
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from . import _strings as strings
from .model_wrapper import DEFAULTS_POOL_ID, TITLE_LENGTH_LIMIT
from .validation import _validate_pool, _validate_title_id, _check_modification_allowed
from .validation import register_error, ValidationError
from .._scoped_session import scoped_session


def do_edit(update: Update, context: CallbackContext) -> Optional[List[ValidationError]]:
    """Change text of the title from the specified pool.

    Expected arguments in context.args:
    'edit' chat_id|'defaults' title_type title_id new_content...
    """
    message: Message = update.effective_message
    if len(context.args) < 5:
        message.reply_markdown_v2(strings.format_more_args(strings.HELP_EDIT))
        return

    errors = []
    pool_id, title_type = _validate_pool(context.args, errors)
    if pool_id is not None:
        user_id = update.effective_user.id
        _check_modification_allowed(pool_id, user_id, context, errors)
    title_id = _validate_title_id(context.args[3], errors)
    new_content = ' '.join(itertools.islice(context.args, 4, None))
    new_content_len = len(new_content)
    if new_content_len > TITLE_LENGTH_LIMIT:
        register_error(errors, strings.ERROR__TITLE_TOO_LONG, limit=TITLE_LENGTH_LIMIT, length=new_content_len)
    if errors:
        return errors
    with scoped_session(context.session_factory) as session:  # type: Session
        title = title_type.get_title(session, pool_id, title_id)
        if title:
            original_text = title.text
            title.text = new_content
            session.commit()
    if title is None:
        error_message = strings.ERROR__NOT_FOUND_IN_TEMPLATES
        error_kwargs = dict(title_id=title_id, type=title_type.value)
        if pool_id is not DEFAULTS_POOL_ID:
            error_message = strings.ERROR__NOT_FOUND_FOR_CHAT
            error_kwargs['chat_id'] = pool_id
        return [ValidationError(error_message, **error_kwargs)]

    original_text = escape_markdown(original_text, version=2)
    message_text = strings.MESSAGE__TITLE_EDITED.format(original_text=original_text)
    message.reply_markdown_v2(message_text)
