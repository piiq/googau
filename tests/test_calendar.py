import pytest
from unittest.mock import patch
from googau.calendar import Calendar
from googau.sessions import CalendarSession


@pytest.fixture
@patch("googau.sessions.CalendarSession.__init__", return_value=None)
def calendar_session(mock_init):
    session = CalendarSession()
    return session


def test_calendar_init(calendar_session):
    calendar = Calendar(session=calendar_session, calendarId="test_calendar_id")
    assert calendar is not None
    assert calendar.calendarId == "test_calendar_id"


@patch("googau.calendar.Calendar.get_events_td", return_value=[])
def test_get_events_td(mock_get_events, calendar_session):
    calendar = Calendar(session=calendar_session, calendarId="test_calendar_id")
    events = calendar.get_events_td()
    assert isinstance(events, list)
    mock_get_events.assert_called_once()
