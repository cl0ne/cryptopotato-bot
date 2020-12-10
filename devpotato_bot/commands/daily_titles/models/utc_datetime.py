import datetime
from typing import Optional

from sqlalchemy import TypeDecorator, DateTime
from sqlalchemy.engine import Dialect

OptDateTime = Optional[datetime.datetime]


class UTCDateTime(TypeDecorator):
    """Makes datetime values timezone-aware (UTC) when fetched from database"""

    impl = DateTime

    def process_result_value(self, value: OptDateTime, dialect: Dialect) -> OptDateTime:
        if value is not None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value
