__ACTIVITY_NAME = '📣Daily 🏅Titles 🎲Assignment'

MESSAGE__DISABLED_FOR_PRIVATE_CHATS = (
    f'*{__ACTIVITY_NAME} is not available for private chats*.\n'
    '\n'
    'It can be enabled for group chats and channels where bot is present.'
)

MESSAGE__ENABLE_REQUIRES_ADMIN = (
    f'{__ACTIVITY_NAME} can be enabled only by administrators'
)
MESSAGE__DISABLE_REQUIRES_ADMIN = (
    f'{__ACTIVITY_NAME} can be disabled only by administrators'
)

MESSAGE__NOT_ENABLED = (
    f'{__ACTIVITY_NAME} <b>is disabled</b> for this chat.\n'
    '\n'
    'It can be enabled by administrator via /daily_titles_start command'
)
POPUP__NOT_ENABLED = f'{__ACTIVITY_NAME} is disabled for this chat'

MESSAGE__ALREADY_ENABLED = (
    f'{__ACTIVITY_NAME} <b>is already enabled</b> for this chat\n'
    '\n'
    'Administrators can disable it via /daily_titles_stop command'
)
MESSAGE__ENABLED = (
    f'{__ACTIVITY_NAME} <b>was enabled</b> for this chat\n'
    '\n'
    'Administrators can disable it via /daily_titles_stop command'
)

MESSAGE__DISABLED = (
    f'{__ACTIVITY_NAME} <b>was disabled</b> for this chat\n'
    '\n'
    'Administrators can enable it via /daily_titles_start command'
)
MESSAGE__ALREADY_DISABLED = (
    f'{__ACTIVITY_NAME} <b>is already disabled</b> for this chat\n'
    '\n'
    'Administrators can enable it via /daily_titles_start command'
)
MESSAGE__WAS_NEVER_ENABLED = (
    f'{__ACTIVITY_NAME} <b>was never enabled</b> for this chat\n'
    '\n'
    'Administrators can enable it via /daily_titles_start command'
)

POPUP__JOINED = f'✊ You have joined {__ACTIVITY_NAME}'
POPUP__ALREADY_JOINED = f'✊ You have already joined {__ACTIVITY_NAME}'

MESSAGE__JOINED = (
    '✊ {mention} has joined\n'
    '\n'
    f'The {__ACTIVITY_NAME}\n'
    '\n'
)
MESSAGE__ALREADY_JOINED = (
    '✊ {mention} has already joined\n'
    '\n'
    f'The {__ACTIVITY_NAME}\n'
    '\n'
)

POPUP__LEFT = f'🚪 You have left {__ACTIVITY_NAME}'
POPUP__NOT_PARTICIPATING = f'◾️ You are not participating in {__ACTIVITY_NAME}'
MESSAGE__LEFT = (
    '🚪 {mention} has left\n'
    '\n'
    f'The {__ACTIVITY_NAME}\n'
    '\n'
)
MESSAGE__NOT_PARTICIPATING = (
    '◾️ {mention} is not participating in\n'
    '\n'
    f'The {__ACTIVITY_NAME}\n'
    '\n'
)

NO_PARTICIPANTS = (
    f"There were no participants in Today's {__ACTIVITY_NAME}\n"
    "\n"
)

MESSAGE__DAILY_TITLES = (
    f"*Today's {__ACTIVITY_NAME}*\n"
    "\n"
    "{assigned_titles}"
)
