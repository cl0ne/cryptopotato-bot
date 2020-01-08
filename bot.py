#!/usr/bin/env python3
#
"""Simple Telegram bot for cryptopotato chat.
"""

import logging
import os
import subprocess
import sys
import traceback

from telegram import Update, Message, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, run_async
from dice_parser import Dice, ParseError, ValueRangeError

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


__NOTATION_DESCRIPTION = (
    'simplified [dice notation](https://en.wikipedia.org/wiki/Dice_notation): `AdB+M`\n'
    '- `A` is a number of rolls (can be omitted if 1)\n'
    '- `B` specifies number of sides\n'
    '- `M` is a  modifier that is added to the roll result, "+" or "-" between `B` and `M` '
    "defines modifier's sign\n"
    'Both `A` and `B` are positive integer numbers, `M` is an integer number, '
    f'maximum number of rolls is *{Dice.ROLL_LIMIT}*, the biggest dice has '
    f'*{Dice.BIGGEST_DICE}* sides'
)


def show_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_markdown(
        '*Available commands:*\n\n'

        '*/me* - announce your actions to the chat\n'
        '\n'
        '*/ping* - check if bot is currently active\n'
        '\n'
        f'*/roll* or */r* - make a dice roll in {__NOTATION_DESCRIPTION}\n'
        '\n'
        '*/fortune* - get a random epigram',
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


def roll_command(update: Update, context: CallbackContext):
    """Perform dice roll specified in dice notation."""
    message: Message = update.message
    if context.args:
        roll_str = context.args[0]
        try:
            dice = Dice.parse(roll_str)
        except ParseError:
            update.message.reply_markdown(
                "Oops, couldn't decide what kind of roll you want to make.\n\n"
                f"This command accepts only {__NOTATION_DESCRIPTION}",
                disable_web_page_preview=True
            )
            return
        except ValueRangeError as e:
            update.message.reply_markdown(e.formatted_message)
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


__developer_ids = []


def produce_error_command(update: Update, context: CallbackContext):
    """Generate error to be handled in error_handler"""
    user_id = update.effective_user.id
    if user_id in __developer_ids:
        assert not 'a banana'
    # ignore everyone else


def error_handler(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
    payload = ''
    user = update.effective_user
    if user:
        payload += f' with user {user.mention_html()}'
    if update.effective_chat:
        payload += f' in chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    if update.poll:
        payload += f' with poll id {update.poll.id}.'
    text = (
        f"Error <code>{context.error}</code> happened{payload}. "
        f"Full traceback:\n\n"
        f"<code>{trace}</code>"
    )
    for dev_id in __developer_ids:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    updater = Updater(token=os.getenv('BOT_TOKEN'), use_context=True)
    developer_ids_str = os.getenv('DEVELOPER_IDS')
    if developer_ids_str:
        try:
            global __developer_ids
            __developer_ids = set(map(int, developer_ids_str.split(',')))
        except ValueError:
            logger.error(
                'DEVELOPER_IDS value must be a comma-separated integers list, not "%s"!',
                developer_ids_str
            )

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", show_help))

    produce_error = CommandHandler(
        "produce_error",
        produce_error_command,
        filters=~Filters.update.edited_message
    )
    dispatcher.add_handler(produce_error)

    me = CommandHandler("me", me_command, filters=~Filters.update.edited_message)
    dispatcher.add_handler(me)

    ping = CommandHandler("ping", ping_command, filters=~Filters.update.edited_message)
    dispatcher.add_handler(ping)

    fortune = CommandHandler("fortune", fortune_command, filters=~Filters.update.edited_message)
    dispatcher.add_handler(fortune)

    roll = CommandHandler(['roll', 'r'], roll_command, filters=~Filters.update.edited_message)
    dispatcher.add_handler(roll)

    dispatcher.add_error_handler(error_handler)

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
