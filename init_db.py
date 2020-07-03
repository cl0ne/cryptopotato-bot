#!/usr/bin/env python3
#
# Use this script to setup fresh database, for existing use alembic migrations!
import logging
import os
import pathlib

from sqlalchemy import create_engine
from devpotato_bot.commands.daily_titles.models.base import Base

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    db_url = os.getenv('DB_URL')
    if db_url is None:
        logger.error('Environment variable DB_URL is not set')
        exit(1)

    from alembic.config import Config
    from alembic import command

    os.chdir(pathlib.Path(__file__).parent)
    alembic_cfg = Config('alembic.ini')

    engine = create_engine(db_url, echo=True)
    Base.metadata.create_all(engine)
    command.stamp(alembic_cfg, "head")
