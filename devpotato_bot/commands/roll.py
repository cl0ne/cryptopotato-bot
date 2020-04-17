from telegram import Update, Message
from telegram.ext import CallbackContext

from ..dice_parser import Dice, ParseError, ValueRangeError

NOTATION_DESCRIPTION = (
    'simplified [dice notation](https://en.wikipedia.org/wiki/Dice_notation): `AdB+M`\n'
    '\\- `A` is a number of rolls \\(can be omitted if 1\\)\n'
    '\\- `B` specifies number of sides, you can put `%` for percentile dice \\(i\\.e\\. `d100`\\)\n'
    '\\- `M` is a modifier that is added to the roll result, "\\+" or "\\-" between `B` and `M` '
    "defines modifier's sign\n"
    'Both `A` and `B` are positive integer numbers, `M` is an integer number, '
    f'maximum number of rolls is *{Dice.ROLL_LIMIT}*, the biggest dice has '
    f'*{Dice.BIGGEST_DICE}* sides'
)


def _roll_callback(update: Update, context: CallbackContext):
    """Perform dice roll specified in dice notation."""
    message: Message = update.message
    if context.args:
        roll_str = context.args[0]
        try:
            dice = Dice.parse(roll_str)
        except ParseError:
            update.message.reply_markdown_v2(
                "Oops, couldn't decide what kind of roll you want to make\\.\n\n"
                f"This command accepts only {NOTATION_DESCRIPTION}",
                disable_web_page_preview=True
            )
            return
        except ValueRangeError as e:
            update.message.reply_markdown_v2(e.formatted_message)
            return
        label = message.text_markdown_v2.split(None, 2)[2:]
        label = label[0] if label else ''
    else:
        roll_str = '1d6'
        dice = Dice(1, 6)
        label = ''
    user_mention = update.effective_user.mention_markdown_v2()
    lines = ['🎲 {} rolls *{}*'.format(user_mention, roll_str)]
    if label:
        lines.extend((' for:\n', label, '\n'))
    lines.append('\n')
    roll_total, single_rolls, was_limited = dice.get_result(item_limit=10)
    lines.extend((
        '\\(',
        ' \\+ '.join(str(r) for r in single_rolls)
    ))
    if was_limited:
        lines.append(' \\+ ⋯ ')
    lines.extend(('\\) \\= ', str(roll_total)))
    text = ''.join(lines)
    message.reply_markdown_v2(text, quote=False, disable_web_page_preview=True)


def get_handler(**kwargs):
    from telegram.ext import Filters, CommandHandler
    return CommandHandler(['roll', 'r'], _roll_callback, filters=~Filters.update.edited_message)
