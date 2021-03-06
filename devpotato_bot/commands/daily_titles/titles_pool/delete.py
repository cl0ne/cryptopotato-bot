import itertools
from typing import Optional, List

from sqlalchemy.orm import Session
from telegram import Update, Message
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from . import _strings as strings
from .model_wrapper import DEFAULTS_POOL_ID
from .validation import _validate_pool, _check_modification_allowed, ValidationError
from .._scoped_session import scoped_session


def do_delete(update: Update, context: CallbackContext) -> Optional[List[ValidationError]]:
    """Delete titles from the specified pool.

    Expected arguments in context.args:
    'delete' chat_id|'defaults' title_type 'all'|(title_id+)
    """
    message: Message = update.effective_message
    if len(context.args) < 4:
        message.reply_markdown_v2(strings.format_more_args(strings.HELP_DELETE))
        return

    errors = []
    pool_id, title_type = _validate_pool(context.args, update.effective_chat, errors)
    if pool_id is not None:
        user_id = update.effective_user.id
        _check_modification_allowed(pool_id, user_id, context, errors)
    if errors:
        return errors

    title_ids_args = itertools.islice(context.args, 3, None)
    delete_all = False
    title_ids, invalid_ids = [], []
    for i in title_ids_args:
        if i.lower() == 'all':
            delete_all = True
            continue
        try:
            title_ids.append(int(i))
        except ValueError:
            invalid_ids.append(i)
    if invalid_ids:
        return [ValidationError(strings.ERROR__INVALID_TITLE_IDS, ids=' '.join(invalid_ids))]
    with scoped_session(context.session_factory) as session:  # type: Session
        deleted_count = title_type.delete(session, pool_id, None if delete_all else title_ids)
        session.commit()
    format_args = dict(type=title_type.value, count=deleted_count)
    message_template = strings.MESSAGE__DELETED_FROM_TEMPLATES
    if pool_id is not DEFAULTS_POOL_ID:
        message_template = strings.MESSAGE__DELETED_FROM_CHAT
        format_args['chat_id'] = escape_markdown(str(pool_id), version=2)
    message.reply_markdown_v2(message_template.format(**format_args))
