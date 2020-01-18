from telegram import Update
from telegram.ext import CallbackContext


def _build_callback(developer_ids):
    def _callback(update: Update, context: CallbackContext):
        """Generate error to be handled in error_handler"""
        user_id = update.effective_user.id
        if user_id in developer_ids:
            assert not 'a banana'
        # ignore everyone else
    return _callback


def get_handler(*, developer_ids, **kwargs):
    from telegram.ext import Filters, CommandHandler
    return CommandHandler(
        "produce_error",
        _build_callback(developer_ids),
        filters=~Filters.update.edited_message
    )
