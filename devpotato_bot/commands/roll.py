from telegram import Update, Message
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from ..dice_parser import Dice, ParseError, ValueRangeError

NOTATION_DESCRIPTION = (
    'The basic formula in the dice notation is `AdB`\\. `A` is a number of dice to be rolled \\(can be omitted if 1'
    '\\)\\. `B` specifies the number of sides the die has, you can use `%` for percentile dice \\(i\\.e\\. '
    f'`d100`\\)\\. The maximum number of rolls is *{Dice.ROLL_LIMIT}*, the biggest allowed dice has *'
    f'{Dice.BIGGEST_DICE}* sides\\.\n '
    '\n'
    'The basic formula can be extended with modifiers:\n'
    '\n'
    'Modifier to keep/discard the lowest/highest `k` results\\. Keep and discard is indicated by modifier\'s sign: `+` '
    'and `-`, omitted sign is equivalent to `+` \\(keep\\)\\. It\'s followed by letter `L` or `H`  and a positive '
    'number to specify which results to be kept/discarded and how many\\. For example, `10d6-L6` discards 6 lowest '
    'results, `10d6+L4` and `10d6L4` keep 4 lowest, `10d6+H5` and `10d6H5` keep 5 highest, `10d6-H3` discards 3 '
    'highest\\.\n '
    '\n'
    'Additive modifier, a number with a sign that is added to \\(or subtracted from\\) total roll result\\. For '
    'example, `d6+5` adds 5 to a single roll result and `5d20L3-2` will subtract 2 from the sum of the 3 lowest '
    'results\\.'
)


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
                f"Oops, couldn't decide what kind of roll you want to make\\.\n"
                f"\n"
                f"{NOTATION_DESCRIPTION}",
                disable_web_page_preview=True
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
    message.reply_markdown_v2(text, quote=False, disable_web_page_preview=True)
