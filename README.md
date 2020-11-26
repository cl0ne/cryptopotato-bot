# Cryptopotato Telegram Bot
Simple [Telegram](https://telegram.org) bot for `cryptopotato` chat. To use this bot in Telegram, [click here](https://telegram.me/devpotato_bot).

## Requirements
* Python version 3.6+ ([type hints](https://www.python.org/dev/peps/pep-0484/) and [f-strings](https://www.python.org/dev/peps/pep-0498/) are used)
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* [cachetools](https://github.com/tkem/cachetools/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [Alembic](https://alembic.sqlalchemy.org/)
* `fortune` executable present in `PATH`

## Setup
### Before first run
Run `python -m devpotato_bot.init_db` to create a new database, make sure package `devpotato_bot` is present in your `sys.path` and `DB_URL` is set (see [Running bot](#running-bot) section for details). Module expects Alembic config file `alembic.ini` to be present in the working directory. Use `ALEMBIC_CFG` environment variable to specify different path.

### Database migrations
To apply schema changes to existing database, [use Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-first-migration). E.g., to get latest version of the schema use command `alembic upgrade head`. Details on specifying database URL can be found [here](alembic/README.md).

### Running bot
You're required to provide the following environment variables:
- `BOT_TOKEN`: bot's authorization token, you can get one for your bot from [BotFather](https://telegram.me/botfather);
- `DB_URL`: [SQLAlchemy database URL](https://docs.sqlalchemy.org/en/13/core/engines.html#engine-configuration).

Below you can find a list of optional environment variables recognized by the bot.

- `DEVELOPER_IDS`

    If you want bot to send error reports directly to your private messages, set `DEVELOPER_IDS` to a comma-separated list of recipient user ids. You can get yours, for example, from [userinfobot](https://t.me/userinfobot) (it supports retrieving ids from forwarded messages too, but it works I suppose only when message's author has enabled linking back to their account in forwarded messages privacy settings). [This question on SO](https://stackoverflow.com/questions/32683992/find-out-my-own-user-id-for-sending-a-message-with-telegram-api) has more options.

    N.B. In order to receive error reports from bot you have to initiate a conversation with the bot first. For example, by issuing `/start` command to it in direct messages or by unblocking the bot if you have blocked it before.

- `DAILY_TITLES_JOB_ENABLED`

    Daily titles assignment job is enabled by default, to explicitly disable or enable it set `DAILY_TITLES_JOB_ENABLED` to 0 or 1, respectively.

- `DAILY_TITLES_JOB_TIME`

    By default, daily titles assignment job is scheduled to run at midnight (timezone depends on `BOT_TIMEZONE` variable), set `DAILY_TITLES_JOB_TIME` to a string in the format `HH[:MM]` to specify a different time. For example, specifying either `09:00` or `9` changes the job's start time to 9 AM.

- `BOT_TIMEZONE`

    Bot's local timezone is UTC by default; to choose a different one, set `BOT_TIMEZONE` to one of the timezone names supported by [`pytz`](https://pypi.org/project/pytz/). For example, `Europe/Kiev`, `US/Pacific`, `Asia/Shanghai`, etc.

To start bot you have to pass its package name with [`-m` option](https://docs.python.org/3/using/cmdline.html#cmdoption-m) to Python interpreter:
```
python -m devpotato_bot
```
Make sure package `devpotato_bot` is present in the `sys.path` (e.g., by adding its parent directory to `PYTHONPATH` environment variable or by changing working directory to it).

## Current Features

### [Emotes](https://en.wikipedia.org/wiki/Emote)

`/me message` announces sender's actions to the chat, original message will be deleted if bot has enough permissions in the chat.

Example use: `/me hit the wall`.

### Fortune

Get a random epigram for yourself with `/fortune`, requires `fortune` executable to be present.


### Dice rolls 🎲

Dice can be rolled with `/roll` (or `/r` for short) command followed by formula (`1d6` used if omitted).

The basic formula in the dice notation is `AdB`. `A` is a number of dice to be rolled (can be omitted if 1). `B` specifies the number of sides the die has, you can use `%` for percentile dice (i.e. `d100`). The maximum number of rolls is 100, the biggest allowed dice has 120 sides.

The basic formula can be extended with modifiers:

Modifier to keep/discard the lowest/highest `k` results. Keep and discard is indicated by modifier's sign: `+` and `-`, omitted sign is equivalent to `+` (keep). It's followed by letter `L` or `H`  and a positive number to specify which results to be kept/discarded and how many. For example, `10d6-L6` discards 6 lowest results, `10d6+L4` and `10d6L4` keep 4 lowest, `10d6+H5` and `10d6H5` keep 5 highest, `10d6-H3` discards 3 highest.

Additive modifier, a number with a sign that is added to (or subtracted from) total roll result. For example, `d6+5` adds 5 to a single roll result and `5d20L3-2` will subtract 2 from the sum of the 3 lowest results.

More info about dice notation and its variations:

- [Wikipedia](https://en.wikipedia.org/wiki/Dice_notation)
- [rolz.org](https://rolz.org/)
- [roll20 wiki](https://wiki.roll20.net/Dice_Reference)
- [openroleplaying.org](https://web.archive.org/web/20061031103919/http://www.openroleplaying.org/tools/dieroller/index.cgi)

### Daily Titles

This activity allows members of group chats to receive random personal titles (e.g. "employee of the day", "follows the white rabbit") every day in the morning. There are two types of titles: _inevitable_ and _shuffled_.

The inevitable titles are always assigned first and are assigned every day in the order they are defined. If chat has enough participants each inevitable title will be assigned to some participant. If there are more participants than inevitable titles, at most 5 random remaining participants will receive random titles from shuffled titles list. If there are enough shuffled titles, each day different set of titles will be assigned.

The activity has to be activated first for the chat by chat administrator with `/daily_titles_start` command (and can be deactivated any time with `/daily_titles_stop`). To participate in the activity, chat member can use `/daily_titles_join` command, command `/daily_titles_leave` allows to cease participation (there are also join/leave buttons under messages with assigned titles). Any user who leaves the chat will be automatically removed from participation.

Every day at a specified time bot will post messages with assigned titles in chats where the activity is active. You can tune this behavior with environment variables described in the [Running bot](#running-bot) section.

Today's assigned titles can be shown on demand with `/daily_titles` command. Which will also make attempt to assign titles if there were no titles assigned today in the current chat. This occurs when the automatic title assignment was disabled, the activity was enabled after the job was running or there were no participants at that time.

Of course, some titles appropriate for members of one chat can be inappropriate for another (they can be seen as not funny or even offensive). That means that there has to be some sort of customization of available titles for every chat. There also has to be a global list of title templates so that every chat can have "default" set of titles.

To make this possible `/titles_pool` command with actions was implemented. Action name is the first argument to this command and there are five available actions: _list_, _add_, _delete_, _edit_ and _help_. When no action specified, help is shown. Each action has its own set of arguments:

- `list chat_id title_type`

    show list of titles with their ids for the corresponding chat

- `list defaults title_type`

    show global template titles

- `add chat_id title_type`

    use as a reply to a message with new titles to add, put each title on a separate line

- `add chat_id title_type defaults`

    copy template titles of type `title_type` to titles of corresponding `chat_id`

- `delete chat_id title_type title_ids`

    delete one or more title for the corresponding chat, `title_ids` is a list of title ids separated by spaces

- `delete chat_id title_type all`

    delete __all__ titles for the corresponding chat

- `edit chat_id title_type title_id new_content`

    change text of title with id `title_id` for the corresponding chat to `new_content`

- `help`

    show this help message


Action arguments:

- `chat_id` is a __numeric id__ of a Telegram chat (you can get it with `/get_chat_id` command from the corresponding chat). You can also use keyword "this" as an alias for current chat id. When referring to global template titles use word "defaults" instead. Note that only users specified in DEVELOPER_IDS are able to edit template titles.

- `title_type` specifies one of two available title types: *inevitable* or *shuffled* (_tip_: you can specify only the prefix of the type name).


### Utility commands

- `/get_chat_id [hide]`

    Shows current chat id, to receive it in private chat with bot use word `hide` as argument.

- `/ping`

    Confirms that bot is currently active by responding with 'pong'.

### Developer commands

Are available only to users specified in `DEVELOPER_IDS`, see [Setup section](#setup) for details, other users are ignored.

- `/produce_error`

    Tests delivery of error reports to developers' private messages by generating an unhandled exception.

- `/dt_participants_refresh`

    Use this when you need to refresh participants and group chats' data (for example, when bot was offline longer than 48 hours and it won't get notification that some users left the chat). It'll disable chats where bot is not present anymore, remove left users from participation, mark participants as "missing" when Telegram for some reason returns "User not found".


## Planned Features

* `/roll` 🚧
    + arbitrary chained rolls (`4+2d6+d10-d7`)
    + exploding rolls (`d6!` or `d10x`), where maximum rolled value triggers extra rolls

## License

Licensed under the [MIT license](LICENSE).
