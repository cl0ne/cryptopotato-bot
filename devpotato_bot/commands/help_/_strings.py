
PAGE_TITLE__HOME = '❔ Help'
PAGE__HOME = (
    '💫🔑🥔❓\n'
    '\n'
    'This bot can do dice rolls in dice notation and assign titles to people'
    ' on a daily basis, there are separate help pages about that\\.\n'
    'Other supported commands include:\n'
    '\n'
    '`/me` \\- announce your actions to the chat otherwise known as'
    ' [emote](https://en.wikipedia.org/wiki/Emote)\\. For example,'
    ' `/me hits the wall`\n'
    '\n'
    '`/ping` \\- check if bot is currently online\n'
    '\n'
    '`/fortune` \\- get a random epigram for yourself\n'
    '\n'
    '`/get_chat_id` \\- Show current chat id'
)

PAGE_TITLE__ROLL = '🎲 Dice rolls'
PAGE__ROLL = (
    '🎲 *Dice rolls* 🎲\n'
    '\n'
    'Dice can be rolled with /roll \\(or /r for short\\) command followed'
    ' by formula \\(`1d6` used if omitted\\)\\.\n'
    '\n'
    'The basic formula in the dice notation is `AdB`\\. `A` is a number of dice'
    ' to be rolled \\(can be omitted if 1\\)\\. `B` specifies the number of'
    ' sides the die has, you can use `%` for percentile dice'
    ' \\(i\\.e\\. `d100`\\)\\. The maximum number of rolls is 100, the biggest'
    ' allowed dice has 120 sides\\.\n'
    '\n'
    'The basic formula can be extended with *modifiers*:\n'
    '\n'
    'Modifier to keep/discard the lowest/highest `k` results\\. Keep and'
    ' discard is indicated by modifier\'s sign: `+` and `-`, omitted sign is'
    ' equivalent to `+` \\(keep\\)\\. It\'s followed by letter `L` or `H`  and'
    ' a positive number to specify which results to be kept/discarded and how'
    ' many\\.\n'
    'For example, `10d6-L6` discards 6 lowest results, `10d6+L4` and'
    ' `10d6L4` keep 4 lowest, `10d6+H5` and `10d6H5` keep 5 highest, `10d6-H3`'
    ' discards 3 highest\\.\n'
    '\n'
    'Additive modifier, a number with a sign that is added to \\(or'
    ' subtracted from\\) total roll result\\.\n'
    'For example, `d6+5` adds 5 to'
    ' a single roll result and `5d20L3-2` will subtract 2 from the sum'
    ' of the 3 lowest results\\.'
)

PAGE_TITLE__DAILY_TITLES = '🏅 Daily titles'
PAGE__DAILY_TITLES = (
    '📣 *Daily 🏅Titles* 🎲\n'
    '\n'
    'This activity allows members of group chats to receive random personal'
    ' titles \\(e\\.g\\. _"employee of the day"_, _"follows the white'
    ' rabbit"_\\) every day in the morning\\. There are two types of titles:'
    ' __inevitable__ and __shuffled__\\.\n'
    '\n'
    'The _inevitable_ titles are always assigned first and are assigned every day'
    ' in the order they are defined\\. If chat has enough participants each'
    ' inevitable title will be assigned to some participant\\. If there are'
    ' more participants than _inevitable_ titles, at most 5 random remaining'
    ' participants will receive random titles from _shuffled_ titles list\\.'
    ' If there are enough _shuffled_ titles, each day different set of titles'
    ' will be assigned\\.\n'
    '\n'
    'The activity has to be activated first for the chat by chat administrator'
    ' with /daily\\_titles\\_start command \\(it can be deactivated any time'
    ' with /daily\\_titles\\_stop\\)\\. To participate in the activity, chat'
    ' member can use /daily\\_titles\\_join command, /daily\\_titles\\_leave'
    ' command allows to cease participation \\(there are also join/leave buttons'
    ' under messages with assigned titles\\)\\. Any user who leaves the chat'
    ' will be automatically removed from participation\\.\n'
    '\n'
    'Every day at 9AM \\(Kyiv time\\) bot will post message with assigned'
    ' titles in chats where activity is active\\. You can get today\'s assigned'
    ' titles with /daily\\_titles command\\. It will make attempt to assign'
    ' titles if there were no titles assigned today \\(activity was enabled'
    ' after 9AM or there were no participants at that time\\)\\.\n'
    '\n'
    'Of course, some titles appropriate for members of one chat can be'
    ' inappropriate for another \\(they can be seen as not funny or even'
    ' offensive\\)\\. For this reason, each chat has own set of titles that'
    ' can be customized by chat administrators and there\'s a global list of'
    ' title templates \\(for now each chat gets a copy of these titles'
    ' when titles are assigned for the first time\\)\\.\n'
    'To customize sets of titles there\'s a /titles\\_pool command with'
    ' five predefined actions passed as a first argument to the command:'
    ' __list__, __add__, __delete__, __edit__ and __help__\\. When no action'
    ' is specified, a help is shown\\. Use `/titles_pool help` to get'
    ' detailed usage for each action\\.'
)
