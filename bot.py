#!/usr/bin/env python3
#
"""Simple Telegram bot for cryptopotato chat.
"""

import logging
import os

from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    bot.send_message(chat_id=update.message.chat_id, text="I'm a useless bot :)")


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('/me - show a message about yourself in the chat')


def me_command(bot, update):
    """Show message about sender."""
    status = update.message.text_html.split(None, 1)[1:]
    status = status[0] if status else 'totally forgot what he wanted to write about'
    name = '<b>***{}</b>'.format(update.effective_user.full_name)
    text = '{} {}'.format(name, status)
    update.message.reply_html(text, quote=False, disable_web_page_preview=True)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token=os.getenv('BOT_TOKEN'))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("me", me_command))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
