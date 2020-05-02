from typing import List, Optional

from telegram.error import BadRequest
from telegram.utils.helpers import escape_markdown

from devpotato_bot.helpers import get_admin_ids
from .model_wrapper import TitleType, DEFAULTS_POOL_ID
from . import _strings as strings


class ValidationError:
    def __init__(self, message: str, *args, **kwargs):
        self.message = message
        self.args = args
        self.kwargs = kwargs

    def format_message(self):
        escaped_args = (
            escape_markdown(str(arg), version=2)
            for arg in self.args
        )
        escaped_kwargs = {
            key: escape_markdown(str(arg), version=2)
            for key, arg in self.kwargs.items()
        }
        return self.message.format(*escaped_args, **escaped_kwargs)


def _validate_pool_id(pool_id: str, errors: List[ValidationError]) -> Optional[int]:
    if pool_id == 'defaults':
        return DEFAULTS_POOL_ID
    try:
        return int(pool_id)
    except ValueError:
        register_error(errors, strings.ERROR__INVALID_CHAT_ID, pool_id)


def _validate_title_type(title_type_prefix: str, errors: List[ValidationError]) -> Optional[TitleType]:
    title_type = TitleType.from_prefix(title_type_prefix)
    if title_type is None:
        register_error(errors, strings.ERROR__INVALID_TITLE_TYPE, title_type_prefix)
    return title_type


def _validate_title_id(title_id: str, errors: List[ValidationError]) -> Optional[int]:
    try:
        return int(title_id)
    except ValueError:
        register_error(errors, strings.ERROR__INVALID_TITLE_ID, title_id)


def _check_modification_allowed(pool_id: Optional[int], user_id: int, context, errors: List[ValidationError]):
    if pool_id is DEFAULTS_POOL_ID:
        not_developer = user_id not in context.developer_ids
        if not_developer:
            register_error(errors, strings.ERROR__CANNOT_EDIT_TEMPLATES)
        return
    try:
        admin_ids = get_admin_ids(context.bot, pool_id)
        if user_id not in admin_ids:
            register_error(errors, strings.ERROR__EDITABLE_BY_CHAT_ADMIN_ONLY)
    except BadRequest:
        register_error(errors, strings.ERROR__BOT_NOT_PRESENT_IN_CHAT, pool_id)


def register_error(errors: List[ValidationError], message, *args, **kwargs):
    errors.append(ValidationError(message, *args, **kwargs))
    return errors
