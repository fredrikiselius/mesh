from datetime import datetime, timezone

import pytest

from mesh.helpers import datetime_from_ISO8601_str, datetime_to_ISO8601_str, zero_pad_year

str_dates = [
    '1-01-01T00:00:00.000Z',
    '11-01-01T00:00:00.000Z'
]

str_dates_year_zero_padded = list(map(zero_pad_year, str_dates))

datetime_dates =[
    datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
    datetime(11, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
]

@pytest.mark.parametrize('str_date, datetime_date', list(zip(str_dates, datetime_dates)))
def test_datetime_from_iso8601_str(str_date, datetime_date):
    assert datetime_from_ISO8601_str(str_date) == datetime_date


@pytest.mark.parametrize('datetime_date, str_date', list(zip(datetime_dates, str_dates_year_zero_padded)))
def test_datetime_to_iso8601_str(datetime_date, str_date):
    assert datetime_to_ISO8601_str(datetime_date) == str_date
