# Cryptopotato Telegram Bot
Simple [Telegram](https://telegram.org) bot for `cryptopotato` chat. To use this bot in Telegram, [click here](https://telegram.me/devpotato_bot).

## Requires
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

## Setup
Bot requires authorization token to be set in `BOT_TOKEN` environment variable. You can get one from [BotFather](https://telegram.me/botfather).

If you want bot send error reports directly to your private messages, set `DEVELOPER_IDS` environment variable to a comma-separated list of corresponding user ids. You can get yours, for example, from [userinfobot](https://t.me/userinfobot) (it supports retrieving ids from forwarded messages too, but it works I suppose only when message's author has enabled linking back to their account in forwarded messages privacy settings). [This question on SO](https://stackoverflow.com/questions/32683992/find-out-my-own-user-id-for-sending-a-message-with-telegram-api) has more options.

## Current Features
* `/me message`
    - Announces sender's actions to the chat, original message will be deleted if bot has enough permissions in the chat.
    - Example: `/me hit the wall`.
* `/fortune`
    - Prints a random epigram, requires `fortune` executable to be present.
* `/ping`
    - Confirms that bot is currently active by responding with 'pong'.
* `/roll` (or `/r` for short)
    - 🚧 make a dice roll in simplified [dice notation](https://en.wikipedia.org/wiki/Dice_notation): `AdB+M`
        - `A`: number of rolls (can be omitted if 1)
        - `B`: number of sides
        - `M`: a modifier that is added to (or subtracted from) roll result ("+" or "-" between `B` and `M` defines modifier's sign)
    - `A`, `B` and `M` are integer numbers, `A` and `B` are positive.
    - Maximum number of rolls is 100, the biggest allowed dice has 120 sides.
* `/produce_error`
    - Test error reporting to developers' private messages by generating an unhandled exception.
    - Is available only to users specified in `DEVELOPER_IDS`, see [Setup section](#setup) for details.

## Planned Features
* `/roll` similar to [RollEm Telegram Bot](https://github.com/treetrnk/rollem-telegram-bot) 🚧
    - arbitrary chained rolls (`4+2d6+d10-d7`)
    - exploding rolls (`d6!` or `d10x`), where maximum rolled value triggers extra rolls
