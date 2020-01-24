import logging
import os

import telegram
from telegram.ext import Updater


class Runner:
    def __init__(self, token, developer_ids=None):
        self.logger = logging.getLogger(__name__)
        self.updater = Updater(token=token, use_context=True)
        self.developer_ids = set() if developer_ids is None else developer_ids

        dispatcher = self.updater.dispatcher

        from .commands import handler_getters
        for handler_getter in handler_getters:
            dispatcher.add_handler(handler_getter(developer_ids=self.developer_ids))

        from devpotato_bot.error_handler import create_callback
        dispatcher.add_error_handler(create_callback(self.developer_ids))

    def run(self):
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()


def main():
    """Start the bot."""
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('Cryptopotato bot started')

    bot_token = os.getenv('BOT_TOKEN')
    developer_ids_str = os.getenv('DEVELOPER_IDS')
    developer_ids = None
    if developer_ids_str:
        try:
            developer_ids = set(map(int, developer_ids_str.split(',')))
        except ValueError:
            logger.error(
                'DEVELOPER_IDS value must be a comma-separated integers list, not "%s"!',
                developer_ids_str
            )
    try:
        Runner(bot_token, developer_ids).run()
    except telegram.error.InvalidToken as e:
        logger.error('Bot token "%s" is not valid', bot_token, exc_info=e)
    except Exception as e:
        logger.error('Unhandled exception', exc_info=e)
