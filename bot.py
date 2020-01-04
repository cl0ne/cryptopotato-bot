#!/usr/bin/env python3
#
"""Simple Telegram bot for cryptopotato chat.
"""

import logging
import os
import subprocess

from telegram import Update, Message
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, run_async

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def show_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_markdown(
        '*Available commands:*\n\n'

        '`/me` - announce your actions to the chat\n'
        '`/ping` - check if bot is currently active\n'
        '`/fortune` - get a random epigram'
    )


def me_command(update: Update, context: CallbackContext):
    """Announce sender's actions to the chat."""
    message: Message = update.message
    status = message.text_html.split(None, 1)[1:]
    status = status[0] if status else 'completely failed to describe his own actions'
    name = '<b>***</b>{}'.format(update.effective_user.mention_html())
    text = '{} {}'.format(name, status)
    message.reply_html(text, quote=False, disable_web_page_preview=True)
    context.bot.delete_message(message.chat_id, message.message_id)


def ping_command(update: Update, context: CallbackContext):
    """Confirm bot's presence in the chat."""
    update.message.reply_text('Pong!')


@run_async
def fortune_command(update: Update, context: CallbackContext):
    """Get random epigram from `fortune`."""
    try:
        result = subprocess.run(['fortune', '-a'], capture_output=True, text=True, timeout=2)
        update.message.reply_text(result.stdout, quote=False, disable_web_page_preview=True)
    except (OSError, TimeoutError) as error:
        logger.warning('Failed to call fortune executable: %s', error)


def error_handler(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    updater = Updater(token=os.getenv('BOT_TOKEN'), use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", show_help))

    me = CommandHandler("me", me_command, filters=~Filters.update.edited_message)
    dispatcher.add_handler(me)

    ping = CommandHandler("ping", ping_command, filters=~Filters.update.edited_message)
    dispatcher.add_handler(ping)

    fortune = CommandHandler("fortune", fortune_command, filters=~Filters.update.edited_message)
    dispatcher.add_handler(fortune)

    dispatcher.add_error_handler(error_handler)

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
