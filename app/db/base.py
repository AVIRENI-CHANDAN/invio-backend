from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import DeclarativeBase

APPLICATION_TIMEZONE = timezone(timedelta(hours=5, minutes=30), name="IST")


def ist_now() -> datetime:
    return datetime.now(APPLICATION_TIMEZONE).replace(microsecond=0)


class Base(DeclarativeBase):
    pass
