import datetime

from sqlalchemy import TypeDecorator, DateTime


class UTCDateTime(TypeDecorator):
    """Provide timezone-aware (UTC) datetime values when fetched from database"""
    impl = DateTime

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value
