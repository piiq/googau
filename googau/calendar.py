"""Calendar utilities."""

import datetime
from typing import Optional
from googau.sessions import CalendarSession


class TimeDeltas:
    """Time deltas constants for calendar events."""

    WTD = datetime.timedelta(days=7)
    MTD = datetime.timedelta(days=30)
    QTD = datetime.timedelta(days=92)
    HTD = datetime.timedelta(days=183)
    YTD = datetime.timedelta(days=365)


class Calendar(object):
    """Gets a Calendar object for the current session and an ID."""

    calendarId = None
    session = None
    events = None

    # pylint: disable=invalid-name
    def __init__(
        self,
        session: Optional[CalendarSession] = None,
        calendarId: Optional[str] = None,
    ):
        """Construct an calendar instance.

        Parameters
        ----------
        session : Union[CalendarSession, None], optional
            The calendar session or None, by default None
        calendarId : Union[str, None], optional
            The calendar id from G-Suite or None, by default None

        """
        self.calendarId = calendarId
        self.service = session

    def get_events_td(
        self, date: Optional[str] = None, time_to_date: str = "ytd", limit: int = 100
    ) -> list:
        """Get calendar events to given date.

        Parameters
        ----------
        date : Optional[str], optional
            The date to get events to, by default None
        time_to_date : str, optional
            The time delta to get events to, by default "ytd"
        limit : int, optional
            The number of events to return, by default 100

        Returns
        -------
        list
            The list of events

        """
        if not date:
            _date = datetime.datetime.utcnow()
            end_date = f"{_date.isoformat()}Z"
        else:
            _date = datetime.datetime.strptime(date, "%Y-%m-%d")
            end_date = f"{_date.isoformat()}Z"
        delta_date = _date - getattr(TimeDeltas, time_to_date.upper())
        start_date = f"{delta_date.isoformat()}Z"
        events_result = self.service.session.list(  # type: ignore
            calendarId=self.calendarId,
            timeMin=start_date,
            timeMax=end_date,
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        self.events = events_result.get("items", [])

        return self.events
