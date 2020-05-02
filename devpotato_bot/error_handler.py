import logging
import sys
import traceback

import telegram
from telegram import Update, ParseMode, Chat, User
from telegram.ext import CallbackContext


def create_callback(developer_ids):
    logger = logging.getLogger(__name__)

    def callback(update: Update, context: CallbackContext):
        """Log Errors caused by Updates."""
        error_str = str(context.error)
        if not error_str:
            error_str = repr(context.error)
        message_parts = [f'An error <code>{error_str}</code> was triggered']

        if update:
            user: User = update.effective_user
            if user:
                message_parts.append(f' by user {user.mention_html()}')

            chat: Chat = update.effective_chat
            if chat:
                if chat.type == 'private':
                    message_parts.append(' in private chat')
                else:
                    message_parts.append(f' in {chat.type} <i>{chat.title}</i>')
                    if update.effective_chat.username:
                        message_parts.append(f' (@{chat.username})')
                message_parts.append(f' (id: {chat.id})')

            if update.poll:
                message_parts.append(f' with poll id {update.poll.id}')

        trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
        if trace:
            message_parts.append(f'. Full traceback:\n\n<code>{trace}</code>')
        message_text = ''.join(message_parts)
        delivery_failed = set()
        for dev_id in developer_ids:
            try:
                context.bot.send_message(dev_id, message_text, parse_mode=ParseMode.HTML)
            except (telegram.error.Unauthorized, telegram.error.BadRequest):
                # User blocked the bot or didn't initiate conversation with it
                delivery_failed.add(dev_id)
        logger.warning('Update "%s" triggered an error', update, exc_info=context.error)

        if delivery_failed:
            failed_ids_str = ' '.join(str(i) for i in delivery_failed)
            text = f'DM error reports delivery failed for users: {failed_ids_str}'
            for dev_id in (developer_ids - delivery_failed):
                try:
                    context.bot.send_message(dev_id, text)
                except (telegram.error.Unauthorized, telegram.error.BadRequest):
                    pass  # just ignore it
            logger.warning(text)
    return callback
