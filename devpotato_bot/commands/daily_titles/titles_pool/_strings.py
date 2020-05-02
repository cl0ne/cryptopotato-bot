TEMPLATE_TITLE_LIST_HEADER = 'Global template titles of type \\({title_type}\\):'
CHAT_TITLE_LIST_HEADER = 'Titles of type \\({title_type}\\) for chat `{chat_id}`:'

NO_TITLES_FOUND = '*none found*'

ERROR__ADD_MUST_BE_REPLY = (
    '*add* action should be used in reply to a message with new titles \\(each title on its own line\\)'
)
ERROR__WRONG_SOURCE_POOL_NAME = 'unexpected value "{}" instead of "defaults"'
ERROR__COPY_TEMPLATES_TO_SELF = 'template title cannot be copied to template titles, sorry'
ERROR__CANNOT_EDIT_TEMPLATES = 'you cannot modify template titles'
ERROR__EDITABLE_BY_CHAT_ADMIN_ONLY = 'Only chat administrators can modify titles for chat'
ERROR__BOT_NOT_PRESENT_IN_CHAT = 'Bot is not present in chat with id `{}`'
ERROR__TITLE_TOO_LONG = 'new title text is too long \\(\\>{limit} chars\\): {length}'
ERROR__TITLES_TOO_LONG = 'these title texts are too long \\(\\>{limit} chars\\): {titles}'
ERROR__NOT_FOUND_FOR_CHAT = 'Title of type \\({type}\\) with id `{title_id}` for chat id `{chat_id}` not found'
ERROR__NOT_FOUND_IN_TEMPLATES = 'Title of type \\({type}\\) with id `{title_id}` not found in global templates'
ERROR__ENABLE_ACTIVITY = 'Daily Titles Assignment activity must be enabled for chat with id `{}`'
ERROR__INVALID_TITLE_IDS = 'These are not valid title ids: {ids}'
ERROR__INVALID_TITLE_ID = 'Unknown value for title\\_id: {}'
ERROR__INVALID_TITLE_TYPE = 'Unknown value for title\\_type: {}'
ERROR__INVALID_CHAT_ID = 'Unknown value for chat\\_id: {}'

HELP_LIST = (
    '*list* `chat_id title_type`\n'
    'show list of titles with their ids for the corresponding chat\n'
    '\n'
    '*list* `defaults title_type`\n'
    'show global template titles'
)

HELP_ADD = (
    '*add* `chat_id title_type`\n'
    'use as a reply to a message with new titles to add, put each title on a separate line\n'
    '\n'
    '*add* `chat_id title_type defaults`\n'
    'copy template titles of type `title_type` to titles of corresponding `chat_id`'
)

HELP_DELETE = (
    '*delete* `chat_id title_type title_ids`\n'
    'delete one or more title for the corresponding chat, `title_ids` is a list of title ids separated by spaces\n'
    '\n'
    '*delete* `chat_id title_type all`\n'
    'delete __all__ titles for the corresponding chat'
)

HELP_EDIT = (
    '*edit* `chat_id title_type title_id new_content`\n'
    'change text of title with id `title_id` for the corresponding chat to `new_content`'
)

MESSAGE__UNKNOWN_ACTION = (
    '"{action}" is not a known action, use */titles\\_pool help*'
    ' to get list of available actions'
)
MESSAGE__NEED_MORE_ARGS = (
    'More arguments required for this action, see usage below\n'
    '\n'
    '{action_help}'
)


def format_more_args(action_help):
    return MESSAGE__NEED_MORE_ARGS.format(action_help=action_help)


MESSAGE__ADDED_TO_TEMPLATES = 'Added to global template \\({type}\\) titles: {count}'
MESSAGE__ADDED_TO_CHAT = 'Added to \\({type}\\) titles of chat `{chat_id}`: {count}'
MESSAGE__DELETED_FROM_TEMPLATES = 'Deleted from global template \\({type}\\) titles: {count}'
MESSAGE__DELETED_FROM_CHAT = 'Deleted \\({type}\\) titles of chat `{chat_id}`: {count}'
MESSAGE__TITLE_EDITED = 'Title text successfully updated, original text: {original_text}'

MESSAGE__HELP = (
    'Title pool management actions:\n'
    '\n'
    f'{HELP_LIST}\n'
    '\n'
    f'{HELP_ADD}\n'
    '\n'
    f'{HELP_DELETE}\n'
    '\n'
    f'{HELP_EDIT}\n'
    '\n'
    '*help*\n'
    'show this help message\n'
    '\n'
    '\n'
    'Action arguments:\n'
    '\n'
    '\\- `chat_id` is a *numeric id* of a Telegram chat \\(you can get it with `/get_chat_id` '
    'command from corresponding chat\\)\\. When referring to global template titles use word *defaults* instead\\.\n'
    '\n'
    '\\- `title_type` specifies one of two available title types: *inevitable* or *shuffled* \\(_tip_: '
    'you can specify only the first letter of the type name\\)'
)
