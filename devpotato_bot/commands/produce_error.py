from devpotato_bot.helpers import developer_only


def get_handler(*, developer_ids, **kwargs):
    from telegram.ext import Filters, CommandHandler

    @developer_only(developer_ids)
    def _callback(update, context):
        """Generate error to be handled in error_handler"""
        assert not 'a banana'

    return CommandHandler(
        "produce_error",
        _callback,
        filters=~Filters.update.edited_message
    )
