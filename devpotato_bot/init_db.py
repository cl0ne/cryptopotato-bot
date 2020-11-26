#!/usr/bin/env python3
#
# Use this script to setup fresh database, for existing ones use alembic migrations!

import logging
import os

from sqlalchemy import create_engine

from .commands.daily_titles.models.base import Base

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    db_url = os.getenv('DB_URL')
    if db_url is None:
        logger.error('Environment variable DB_URL is not set')
        exit(1)

    alembic_cfg_path = os.getenv('ALEMBIC_CFG', 'alembic.ini')
    if not os.path.isfile(alembic_cfg_path):
        logger.error('Alembic config file is not found at "%s"', alembic_cfg_path)
        exit(1)

    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config(alembic_cfg_path)

    engine = create_engine(db_url, echo=True)
    Base.metadata.create_all(engine)
    command.stamp(alembic_cfg, "head")
