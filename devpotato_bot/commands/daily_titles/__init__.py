def register_handlers(runner):
    from ._common import CommandHandler as DTCommandHandler
    from telegram.ext import Filters
    dispatcher = runner.updater.dispatcher

    from . import join, leave, start, stop
    for command, m in [
        ('daily_titles_stop', stop),
        ('daily_titles_start', start),
        ('daily_titles_join', join),
        ('daily_titles_leave', leave)
    ]:
        dispatcher.add_handler(DTCommandHandler(
            command,
            m.command_callback,
            extra_context={'session_factory': runner.session_factory}
        ))
        runner.add_command_description(command, m.COMMAND_DESCRIPTION)

    from . import titles_pool
    titles_pool.register_handlers(runner)

    from . import show
    dispatcher.add_handler(DTCommandHandler(
        'daily_titles',
        show.command_callback,
        filters=~Filters.update.edited_message,
        extra_context={'session_factory': runner.session_factory}
    ))
    runner.add_command_description('daily_titles', show.COMMAND_DESCRIPTION)

    from devpotato_bot.base_handlers import CommandHandler
    from . import refresh_participants
    dispatcher.add_handler(CommandHandler(
        'dt_participants_refresh',
        refresh_participants.command_callback,
        filters=~Filters.update.edited_message,
        extra_context={
            'session_factory': runner.session_factory,
            'developer_ids': runner.developer_ids
        }
    ))

    from devpotato_bot.base_handlers import CallbackQueryHandler
    dispatcher.add_handler(CallbackQueryHandler(
        leave.button_callback,
        pattern='^daily_titles.leave$',
        extra_context={'session_factory': runner.session_factory}
    ))
    dispatcher.add_handler(CallbackQueryHandler(
        join.button_callback,
        pattern='^daily_titles.join$',
        extra_context={'session_factory': runner.session_factory}
    ))

    from devpotato_bot.base_handlers import MessageHandler
    from . import user_leave_chat
    dispatcher.add_handler(MessageHandler(
        Filters.status_update.left_chat_member,
        user_leave_chat.message_callback,
        extra_context={'session_factory': runner.session_factory}
    ))
    from . import group_migrated
    dispatcher.add_handler(MessageHandler(
        Filters.status_update.migrate,
        group_migrated.message_callback,
        extra_context={'session_factory': runner.session_factory}
    ))
