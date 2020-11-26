def register_handlers(runner):
    from telegram.ext import Filters
    dispatcher = runner.updater.dispatcher

    from . import fortune, me, ping, roll
    from telegram.ext import CommandHandler

    dispatcher.add_handler(CommandHandler(
        'fortune', fortune.command_callback,
        filters=~Filters.update.edited_message,
        run_async=True
    ))
    runner.add_command_description('fortune', fortune.COMMAND_DESCRIPTION)

    dispatcher.add_handler(CommandHandler(
        'me', me.command_callback,
        filters=~Filters.update.edited_message
    ))
    runner.add_command_description('me', me.COMMAND_DESCRIPTION)

    dispatcher.add_handler(CommandHandler(
        'ping', ping.command_callback,
        filters=~Filters.update.edited_message
    ))
    runner.add_command_description('ping', ping.COMMAND_DESCRIPTION)

    dispatcher.add_handler(CommandHandler(
        ['roll', 'r'], roll.command_callback,
        filters=~Filters.update.edited_message
    ))
    runner.add_command_description('r', roll.COMMAND_DESCRIPTION)
    runner.add_command_description('roll', roll.COMMAND_DESCRIPTION)

    # Developer commands
    from . import get_chat_id, produce_error
    from devpotato_bot.base_handlers import CommandHandler
    dispatcher.add_handler(CommandHandler(
        'get_chat_id',
        get_chat_id.command_callback,
        filters=~Filters.update.edited_message,
        extra_context={'developer_ids': runner.developer_ids}
    ))
    runner.add_command_description('get_chat_id', get_chat_id.COMMAND_DESCRIPTION)

    dispatcher.add_handler(CommandHandler(
        'produce_error',
        produce_error.command_callback,
        filters=~Filters.update.edited_message,
        extra_context={'developer_ids': runner.developer_ids}
    ))

    from . import daily_titles
    daily_titles.register_handlers(runner)

    from .help_ import HelpPages
    HelpPages().register_handlers(runner)
