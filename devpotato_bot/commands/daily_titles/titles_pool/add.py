from typing import Optional, List

from sqlalchemy.orm import Session
from telegram import Update, Message
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from . import _strings as strings
from .model_wrapper import DEFAULTS_POOL_ID, TITLE_LENGTH_LIMIT
from .validation import _validate_pool, _check_modification_allowed
from .validation import register_error, ValidationError
from .._scoped_session import scoped_session


def do_add(update: Update, context: CallbackContext) -> Optional[List[ValidationError]]:
    """Add new titles to the specified pool.

    Expected arguments in context.args:
    'add' chat_id|'defaults' title_type ['defaults']
    """
    message: Message = update.effective_message
    if len(context.args) < 3:
        reply_text = strings.MESSAGE__NEED_MORE_ARGS.format(action_help=strings.HELP_ADD)
        message.reply_markdown_v2(reply_text)
        return

    errors = []
    pool_id, title_type = _validate_pool(context.args, update.effective_chat, errors)
    from_defaults = False
    if len(context.args) > 3:
        source_pool = context.args[3].lower()
        if source_pool != 'defaults':
            register_error(errors, strings.ERROR__WRONG_SOURCE_POOL_NAME, source_pool)
            from_defaults = None
        else:
            from_defaults = True
    if from_defaults is False and message.reply_to_message is None:
        register_error(errors, strings.ERROR__ADD_MUST_BE_REPLY)
    if pool_id is DEFAULTS_POOL_ID and from_defaults:
        register_error(errors, strings.ERROR__COPY_TEMPLATES_TO_SELF)
    if pool_id is not None:
        user_id = update.effective_user.id
        _check_modification_allowed(pool_id, user_id, context, errors)
    if errors:
        return errors

    title_lines = []
    if not from_defaults:
        trimmed_lines = map(str.strip, message.reply_to_message.text.splitlines())
        title_lines = list(filter(None, trimmed_lines))
        too_long_lines = [i + 1 for i, line in enumerate(title_lines)
                          if len(line) > TITLE_LENGTH_LIMIT]
        if too_long_lines:
            too_long_lines_str = ' '.join(map(str, too_long_lines))
            return [ValidationError(strings.ERROR__TITLES_TOO_LONG,
                                    limit=TITLE_LENGTH_LIMIT, titles=too_long_lines_str)]

    with scoped_session(context.session_factory) as session:  # type: Session
        if pool_id is not DEFAULTS_POOL_ID:
            from ..models import GroupChat
            chat_data = GroupChat.get_by_id(session, pool_id)
            if chat_data is None or not chat_data.is_enabled:
                return [ValidationError(strings.ERROR__ENABLE_ACTIVITY, pool_id)]
        if from_defaults:
            new_title_count = title_type.copy_defaults(session, pool_id)
        else:
            title_type.add_list(session, pool_id, title_lines)
            new_title_count = len(title_lines)
        session.commit()
    format_args = dict(type=title_type.value, count=new_title_count)
    message_template = strings.MESSAGE__ADDED_TO_TEMPLATES
    if pool_id is not DEFAULTS_POOL_ID:
        message_template = strings.MESSAGE__ADDED_TO_CHAT
        format_args['chat_id'] = escape_markdown(str(pool_id), version=2)
    message.reply_markdown_v2(message_template.format(**format_args))
