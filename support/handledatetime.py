import datetime
import pytz


local_tz = 'Europe/Amsterdam'

def set_localtime(tz):
    local_tz = tz

def localize_datetime(dt: datetime.datetime) -> datetime.datetime:
    return pytz.timezone(local_tz).localize(dt)

def parse_datetime_isoformat(iso_datetime_str: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(iso_datetime_str)