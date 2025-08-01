from utils.helpers import format_datetime

def test_format_datetime_iso():
    assert format_datetime("2024-04-01T15:30:00") == "01/04/2024"

def test_format_datetime_invalid():
    assert format_datetime(None) == "--/--/----"