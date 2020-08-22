from typing import Optional, List

from sqlalchemy.orm import Query, Session
from telegram import Update, Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from . import _strings as strings
from .model_wrapper import DEFAULTS_POOL_ID, paginate_query
from .validation import _validate_pool, ValidationError
from .._scoped_session import scoped_session

MESSAGE_DATA_KEY = 'titles_pool.show'


def do_list(update: Update, context: CallbackContext) -> Optional[List[ValidationError]]:
    """Show list of titles from the specified pool.

    Expected arguments in context.args:
    'list' chat_id|'defaults' title_type
    """
    message: Message = update.effective_message
    if len(context.args) < 3:
        message.reply_markdown_v2(strings.format_more_args(strings.HELP_LIST))
        return

    errors = []
    pool_id, title_type = _validate_pool(context.args, errors)
    if errors:
        return errors

    with scoped_session(context.session_factory) as session:  # type: Session
        titles_query: Query = title_type.query_select(session, pool_id)
        titles, page, page_count = paginate_query(titles_query)
    reply_formatted = format_page(pool_id, title_type, page, page_count, titles)
    sent_message: Message = message.reply_text(**reply_formatted)
    if page_count > 1:
        message_data = context.chat_data.setdefault(MESSAGE_DATA_KEY, {})
        message_data[sent_message.message_id] = (title_type, pool_id, page, page_count)


def list_show_page(update, context: CallbackContext):
    """"Show next/previous page of the titles list"""
    callback_query: CallbackQuery = update.callback_query
    message_data: dict = context.chat_data.setdefault(MESSAGE_DATA_KEY, {})
    message_id = callback_query.message.message_id
    list_context = message_data.get(message_id)
    if list_context is None:
        return
    title_type, pool_id, page, page_count = list_context
    go_forward = context.match[1] == 'next'
    if go_forward:
        page += 1
    else:
        page -= 1
    with scoped_session(context.session_factory) as session:  # type: Session
        titles_query: Query = title_type.query_select(session, pool_id)
        titles, page, page_count = paginate_query(titles_query, page, page_count)

    reply_formatted = format_page(pool_id, title_type, page, page_count, titles)
    callback_query.edit_message_text(**reply_formatted)
    if page_count > 1:
        message_data[message_id] = (title_type, pool_id, page, page_count)
    else:
        del message_data[message_id]


def format_page(pool_id, title_type, page, page_count, titles):
    has_after = page < page_count
    has_before = page > 1
    buttons = []
    if has_before:
        buttons.append(InlineKeyboardButton("Previous page", callback_data='titles:list:prev'))
    if has_after:
        buttons.append(InlineKeyboardButton("Next page", callback_data='titles:list:next'))
    if titles:
        titles_str = '\n'.join(
            f'`{escape_markdown(str(t.id), version=2)}` {escape_markdown(t.text, version=2)}'
            for t in titles
        )
    else:
        titles_str = strings.NO_TITLES_FOUND
    if pool_id is DEFAULTS_POOL_ID:
        header = strings.TEMPLATE_TITLE_LIST_HEADER.format(title_type=title_type.value)
    else:
        header = strings.CHAT_TITLE_LIST_HEADER.format(title_type=title_type.value, chat_id=pool_id)
    message_lines = [header, '', titles_str]
    if page_count > 1:
        message_lines.extend(('', f'page: {page} / {page_count}'))
    message_text = '\n'.join(message_lines)
    reply_markup = InlineKeyboardMarkup.from_row(buttons) if buttons else None
    return dict(text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
