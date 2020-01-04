#!/usr/bin/env python3
#
"""Simple Telegram bot for cryptopotato chat.
"""

import logging
import os
import subprocess

from telegram import Update, Message
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, run_async
from dice_parser import Dice


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def show_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_markdown(
        '*Available commands:*\n\n'

        '`/me` - announce your actions to the chat\n'
        '\n'
        '`/ping` - check if bot is currently active\n'
        '\n'
        '`/roll` - make a dice roll in simplified '
        '[dice notation](https://en.wikipedia.org/wiki/Dice_notation): `AdX`\n'
        'Here `A` stands for number of rolls (can be omitted if 1) and `X` for number of sides; '
        'both `A` and `X` are positive integer numbers\n'
        '\n'
        '`/fortune` - get a random epigram',
        disable_web_page_preview=True
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


def roll_command(update: Update, context: CallbackContext):
    """Perform dice roll specified in dice notation."""
    message: Message = update.message
    if context.args:
        roll_str = context.args[0]
        try:
            dice = Dice.parse(roll_str)
        except ValueError:
            update.message.reply_markdown(
                "Oops, couldn't decide what kind of roll you want to make.\n\n"
                "This command accepts simplified [dice notation]"
                "(https://en.wikipedia.org/wiki/Dice_notation): `AdX`\n"
                "where `A` stands for number of rolls (can be omitted if 1) and "
                "`X` for number of sides; both `A` and `X` are positive integer numbers\n",
                disable_web_page_preview=True
            )
            return
        label = message.text_markdown.split(None, 2)[2:]
        label = label[0] if label else ''
    else:
        roll_str = '1d6'
        dice = Dice(1, 6)
        label = ''
    lines = ['{} rolls *{}*'.format(update.effective_user.mention_markdown(), roll_str)]
    if label:
        lines.extend((' for:\n', label, '\n'))
    lines.append('\n')
    roll_total, single_rolls, was_limited = dice.get_result(item_limit=10)
    lines.extend((
        '(',
        ' + '.join(str(r) for r in single_rolls)
    ))
    if was_limited:
        lines.append(' ... ')
    lines.extend((') = ', str(roll_total)))
    text = ''.join(lines)
    message.reply_markdown(text, quote=False, disable_web_page_preview=True)


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

    roll = CommandHandler("roll", roll_command, filters=~Filters.update.edited_message)
    dispatcher.add_handler(roll)

    dispatcher.add_error_handler(error_handler)

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
