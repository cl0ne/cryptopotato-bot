def register_handlers(runner):
    from telegram.ext import Filters
    dispatcher = runner.updater.dispatcher

    from . import fortune, help, me, ping, roll
    from telegram.ext import CommandHandler
    dispatcher.add_handler(CommandHandler(
        "fortune", fortune.command_callback,
        filters=~Filters.update.edited_message
    ))
    dispatcher.add_handler(CommandHandler(
        "help", help.command_callback
    ))
    dispatcher.add_handler(CommandHandler(
        "me", me.command_callback,
        filters=~Filters.update.edited_message
    ))
    dispatcher.add_handler(CommandHandler(
        "ping", ping.command_callback,
        filters=~Filters.update.edited_message
    ))
    dispatcher.add_handler(CommandHandler(
        ['roll', 'r'], roll.command_callback,
        filters=~Filters.update.edited_message
    ))

    # Developer commands
    from . import get_chat_id, produce_error
    from devpotato_bot.base_handlers import CommandHandler
    dispatcher.add_handler(CommandHandler(
        "get_chat_id",
        get_chat_id.command_callback,
        filters=~Filters.update.edited_message,
        extra_context={'developer_ids': runner.developer_ids}
    ))
    dispatcher.add_handler(CommandHandler(
        "produce_error",
        produce_error.command_callback,
        filters=~Filters.update.edited_message,
        extra_context={'developer_ids': runner.developer_ids}
    ))

    from . import daily_titles
    daily_titles.register_handlers(runner)
