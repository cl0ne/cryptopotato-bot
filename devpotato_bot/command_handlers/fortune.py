import logging
import subprocess

from telegram import Update
from telegram.ext import CallbackContext, run_async

_logger = logging.getLogger(__name__)


@run_async
def _fortune_callback(update: Update, context: CallbackContext):
    """Get random epigram from `fortune`."""
    try:
        result = subprocess.run(['fortune', '-a'], capture_output=True, text=True, timeout=2)
        update.message.reply_text(result.stdout, quote=False, disable_web_page_preview=True)
    except (OSError, TimeoutError) as error:
        _logger.warning('Failed to call fortune executable: %s', error)


def get_handler(**kwargs):
    from telegram.ext import Filters, CommandHandler
    return CommandHandler("fortune", _fortune_callback, filters=~Filters.update.edited_message)
