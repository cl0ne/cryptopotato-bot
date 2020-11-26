import datetime
import logging
import os
import sys
from typing import Set, Dict, Optional

import pytz
import telegram
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import Bot
from telegram.ext import Updater, Defaults
from dataclasses import dataclass, field

# noinspection PyUnresolvedReferences
from . import sqlite_fk  # enable foreign key support for SQLite


@dataclass
class RunnerConfig:
    bot_token: str
    db_url: str
    daily_titles_job_enabled: bool = True
    developer_ids: Set[int] = field(default_factory=set)
    bot_timezone: pytz.BaseTzInfo = pytz.utc
    daily_titles_job_time: datetime.time = datetime.time()

    @staticmethod
    def from_env(env: Dict[str, str]) -> Optional['RunnerConfig']:
        logger = logging.getLogger(__name__)
        config = RunnerConfig(env.get('BOT_TOKEN'), env.get('DB_URL'))
        fail = False

        if tz_name := env.get('BOT_TIMEZONE'):
            try:
                config.bot_timezone = pytz.timezone(tz_name)
            except pytz.UnknownTimeZoneError:
                logger.error('BOT_TIMEZONE value "%s" is not a valid timezone name', tz_name)
                fail = True
        if enable_job_str := env.get('DAILY_TITLES_JOB_ENABLED'):
            try:
                config.daily_titles_job_enabled = bool(int(enable_job_str))
            except ValueError:
                logger.error('DAILY_TITLES_JOB_ENABLED value "%s" does not correspond to 0 or 1', enable_job_str)
                fail = True
        if time_str := env.get('DAILY_TITLES_JOB_TIME'):
            try:
                time_args = map(int, time_str.split(':'))
                config.daily_titles_job_time = datetime.time(*time_args)
            except ValueError as e:
                logger.error(
                    'DAILY_TITLES_JOB_TIME value "%s" does not represent a valid time: %s',
                    time_str, e.args[0]
                )
                fail = True
        if developer_ids_str := env.get('DEVELOPER_IDS'):
            try:
                config.developer_ids = set(map(int, developer_ids_str.split(',')))
            except ValueError:
                logger.error(
                    'DEVELOPER_IDS value "%s" is not a valid comma-separated list of integers',
                    developer_ids_str
                )
                fail = True
        return None if fail else config


class Runner:
    DAILY_TITLES_JOB_NAME = 'assign titles'

    def __init__(self, config: RunnerConfig):
        self.logger = logging.getLogger(__name__)
        bot_defaults = Defaults(disable_web_page_preview=True, tzinfo=config.bot_timezone)
        self.updater = Updater(token=config.bot_token, defaults=bot_defaults)
        self.engine = create_engine(config.db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.developer_ids = config.developer_ids

        self._command_list = dict()
        from . import commands
        commands.register_handlers(self)
        bot: Bot = self.updater.bot
        bot.set_my_commands(self._command_list.items())

        dispatcher = self.updater.dispatcher
        from devpotato_bot.error_handler import create_callback
        dispatcher.add_error_handler(create_callback(self.developer_ids))

        logger = logging.getLogger(__name__)
        if config.daily_titles_job_enabled:
            job_time = config.daily_titles_job_time
            logger.info('Scheduling daily titles assignment job @ %s', job_time)
            from .commands.daily_titles.daily_job import job_callback
            job_queue = self.updater.job_queue
            job_queue.run_daily(job_callback, job_time,
                                context=self.session_factory,
                                name=Runner.DAILY_TITLES_JOB_NAME)
        else:
            logger.info('Daily titles assignment job was disabled')

    def add_command_description(self, command, description):
        """Add command to the list of commands to be shown to Telegram clients"""
        self._command_list[command] = description

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
    config = RunnerConfig.from_env(os.environ)
    if config is None:
        logger.error('Failed to create runner config')
        sys.exit(-1)
    try:
        Runner(config).run()
    except telegram.error.InvalidToken as e:
        logger.error('Bot token "%s" is not valid', config.bot_token, exc_info=e)
    except Exception as e:
        logger.error('Unhandled exception', exc_info=e)
    else:
        return
    sys.exit(-1)
