# Cryptopotato Telegram Bot
Simple [Telegram](https://telegram.org) bot for `cryptopotato` chat. To use this bot in Telegram, [click here](https://telegram.me/devpotato_bot).

## Requires
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

## Setup
Bot requires authorization token to be set in `BOT_TOKEN` environment variable. You can get one from [BotFather](https://telegram.me/botfather).

## Current Features
* `/me message`
    - Announces sender's actions to the chat, original message will be deleted if bot has enough permissions in the chat.
    - Example: `/me hit the wall`
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

## Planned Features
* `/roll` similar to [RollEm Telegram Bot](https://github.com/treetrnk/rollem-telegram-bot) 🚧
    - arbitrary chained rolls (`4+2d6+d10-d7`)
    - exploding rolls (`d6!` or `d10x`), where maximum rolled value triggers extra rolls
