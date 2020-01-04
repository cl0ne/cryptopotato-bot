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
* `/roll`
    - 🚧 make a dice roll in simplified [dice notation](https://en.wikipedia.org/wiki/Dice_notation): `AdX`, where `A` stands for number of rolls (can be omitted if 1) and `X` for number of sides; both `A` and `X` are positive integer numbers. Currently both numbers  are not limited.

## Planned Features
* `/roll` similar to [RollEm Telegram Bot](https://github.com/treetrnk/rollem-telegram-bot)
