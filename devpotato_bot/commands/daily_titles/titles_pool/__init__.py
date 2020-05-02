from telegram import Update
from telegram.ext import CallbackContext, Filters
from telegram.utils.helpers import escape_markdown

from . import _strings as strings
from .add import do_add
from .delete import do_delete
from .edit import do_edit
from .show import do_list, list_show_page
from .validation import ValidationError


def do_help(update: Update, _context: CallbackContext):
    update.effective_message.reply_markdown_v2(strings.MESSAGE__HELP)


def unknown_action(update: Update, context: CallbackContext):
    action_name = escape_markdown(context.args[0], version=2)
    message_text = strings.MESSAGE__UNKNOWN_ACTION.format(action=action_name)
    update.effective_message.reply_markdown_v2(message_text)


_actions = {
    'list': do_list,
    'add': do_add,
    'delete': do_delete,
    'edit': do_edit,
    'help': do_help,
}


def command_callback(update: Update, context: CallbackContext):
    """Announce current daily titles to the chat."""
    if context.args:
        action_name = context.args[0].lower()
        action = _actions.get(action_name, unknown_action)
    else:
        action = do_help
    errors = action(update, context)
    if errors:
        reply_text = '\n\n'.join(e.format_message() for e in errors)
        update.effective_message.reply_markdown_v2(reply_text)


def register_handlers(runner):
    from devpotato_bot.base_handlers import CommandHandler
    from devpotato_bot.base_handlers import CallbackQueryHandler
    dispatcher = runner.updater.dispatcher
    dispatcher.add_handler(CommandHandler(
        "titles_pool",
        command_callback,
        filters=~Filters.update.edited_message,
        extra_context={
            'session_factory': runner.session_factory,
            'developer_ids': runner.developer_ids
        }
    ))
    dispatcher.add_handler(CallbackQueryHandler(
        list_show_page,
        pattern='^titles:list:(prev|next)$',
        extra_context={'session_factory': runner.session_factory}
    ))
