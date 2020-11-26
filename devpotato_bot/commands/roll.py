from telegram import Update, Message
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from ..dice_parser import Dice, ParseError, ValueRangeError

COMMAND_DESCRIPTION = 'Roll some dice (use dice notation)'


def format_range_error(e: ValueRangeError):
    format_args = {'arg_name': e.arg_name, 'value': e.value}
    if e.allowed_range == (None, None):
        format_str = '{arg_name} has unacceptable value: {value}'
    else:
        arg_min, arg_max = e.allowed_range
        if arg_max is None:
            format_args.update(arg_min=arg_min)
            format_str = '{arg_name} is less than {arg_min}: {value}'
        elif arg_min is None:
            format_args.update(arg_max=arg_max)
            format_str = '{arg_name} is greater than {arg_max}: {value}'
        else:
            format_args.update(arg_max=arg_max, arg_min=arg_min)
            format_str = '{arg_name} is not between {arg_min} and {arg_max}: {value}'
    return format_str.format(**{
        k: escape_markdown(str(v), version=2)
        for k, v in format_args.items()
    })


def command_callback(update: Update, context: CallbackContext):
    """Perform dice roll specified in dice notation."""
    message: Message = update.message
    if context.args:
        roll_str = context.args[0]
        try:
            dice = Dice.parse(roll_str)
        except ParseError:
            message.reply_markdown_v2(
                "Oops, couldn't decide what kind of roll you want to make\\.\n"
                "\n"
                "See /help for the detailed description of the supported notation"
            )
            return
        except ValueRangeError as e:
            message.reply_markdown_v2(format_range_error(e))
            return
        label = message.text_markdown_v2.split(None, 2)[2:]
        label = label[0] if label else ''
        roll_str = escape_markdown(roll_str, version=2)
    else:
        roll_str = '1d6'
        dice = Dice(1, 6)
        label = ''
    user_mention = update.effective_user.mention_markdown_v2()
    lines = ['🎲 {} rolls *{}*'.format(user_mention, roll_str)]
    if label:
        lines.extend((' for:\n', label, '\n'))
    lines.append('\n')
    roll_total, single_rolls, was_limited = dice.get_results(item_limit=15)
    if dice.modifier:
        lines.extend(escape_markdown(f'{dice.modifier} + ', version=2))
    lines.extend((
        '\\(',
        ' \\+ '.join(
            f'~{r.value}~' if r.is_discarded else f'*__{r.value}__*'
            for r in single_rolls
        )
    ))
    if was_limited:
        lines.append(' \\+ ⋯ ')
    lines.extend(('\\) \\= ', str(roll_total)))
    text = ''.join(lines)
    message.reply_markdown_v2(text, quote=False)
