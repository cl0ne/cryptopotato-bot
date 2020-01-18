import logging
import sys
import traceback

import telegram
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

_logger = logging.getLogger(__name__)


def create_callback(developer_ids):
    def callback(update: Update, context: CallbackContext):
        """Log Errors caused by Updates."""
        message_parts = [f'<code>{context.error!r}</code> was triggered']

        user = update.effective_user
        if user:
            message_parts.append(f' by user {user.mention_html()}')

        chat = update.effective_chat
        if chat:
            if chat.type == 'private':
                message_parts.append(' in private chat')
            else:
                message_parts.append(f' in {chat.type} <i>{update.effective_chat.title}</i>')
                if update.effective_chat.username:
                    message_parts.append(f' (@{update.effective_chat.username})')

        if update.poll:
            message_parts.append(f' with poll id {update.poll.id}')

        trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
        message_parts.append(f'. Full traceback:\n\n<code>{trace}</code>')
        message_text = ''.join(message_parts)
        delivery_failed = set()
        for dev_id in developer_ids:
            try:
                context.bot.send_message(dev_id, message_text, parse_mode=ParseMode.HTML)
            except (telegram.error.Unauthorized, telegram.error.BadRequest):
                # User blocked the bot or didn't initiate conversation with it
                delivery_failed.add(dev_id)
        _logger.warning('Update "%s" caused error "%s"', update, context.error)

        if delivery_failed:
            failed_ids_str = ' '.join(str(i) for i in delivery_failed)
            text = f'DM error reports delivery failed for users: {failed_ids_str}'
            for dev_id in (developer_ids - delivery_failed):
                try:
                    context.bot.send_message(dev_id, text)
                except (telegram.error.Unauthorized, telegram.error.BadRequest):
                    pass  # just ignore it
            _logger.warning(text)
    return callback
