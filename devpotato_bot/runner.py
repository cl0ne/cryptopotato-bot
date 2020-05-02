import datetime
import logging
import os

import telegram
from dateutil import tz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.ext import Updater

# noinspection PyUnresolvedReferences
from . import sqlite_fk  # enable foreign key support for SQLite


class Runner:
    DAILY_TITLES_POST_TIME = datetime.time(hour=9, tzinfo=tz.gettz('Europe/Kiev'))
    DAILY_TITLES_JOB_NAME = 'assign titles'

    def __init__(self, token: str, db_url: str, titles_daily_job_enabled: bool = True, developer_ids=None):
        self.logger = logging.getLogger(__name__)
        self.updater = Updater(token=token, use_context=True)
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.developer_ids = set() if developer_ids is None else developer_ids

        from . import commands
        commands.register_handlers(self)

        dispatcher = self.updater.dispatcher
        from devpotato_bot.error_handler import create_callback
        dispatcher.add_error_handler(create_callback(self.developer_ids))

        logger = logging.getLogger(__name__)
        if titles_daily_job_enabled:
            job_time = Runner.DAILY_TITLES_POST_TIME
            logger.info('Scheduling daily titles assignment job @ %s', job_time)
            from .commands.daily_titles.daily_job import job_callback
            job_queue = self.updater.job_queue
            job_queue.run_daily(job_callback, job_time,
                                context=self.session_factory,
                                name=Runner.DAILY_TITLES_JOB_NAME)
        else:
            logger.info('Daily titles assignment job was disabled')

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
    db_url = os.getenv('DB_URL')
    developer_ids_str = os.getenv('DEVELOPER_IDS')
    titles_daily_job_enabled = int(os.getenv('TITLES_DAILY_JOB_ENABLED', 1))
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
        Runner(bot_token, db_url, titles_daily_job_enabled, developer_ids).run()
    except telegram.error.InvalidToken as e:
        logger.error('Bot token "%s" is not valid', bot_token, exc_info=e)
    except Exception as e:
        logger.error('Unhandled exception', exc_info=e)
