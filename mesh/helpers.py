from datetime import datetime, timezone


ISO8601_DATE_STR = '%Y-%m-%dT%H:%M:%S.%fZ'
TRAKT_TIMESTR = ISO8601_DATE_STR


def datetime_from_ISO8601_str(date_str):
    """Parse ISO8601 formatted `:class:str` to `:class:datetime.datetime`"""
    return datetime.strptime(date_str, ISO8601_DATE_STR).replace(tzinfo=timezone.utc)


def datetime_to_ISO8601_str(datetime_obj):
    """Returns ISO8601 `:class:str` from `:class:datetime.datetime`"""
    return datetime_obj.replace(microsecond=0).strftime(ISO8601_DATE_STR)[:-4] + 'Z'
