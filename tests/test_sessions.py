"""Test the sessions module."""

from unittest.mock import patch
import pytest
from googau.sessions import (
    GmailSession,
    SheetsSession,
    DocSession,
    DriveSession,
    FilesSession,
    CalendarSession,
)

# pylint: disable=import-outside-toplevel


@pytest.mark.parametrize(
    "session_class",
    [
        "GoogleSession",
        "SheetsSession",
        "DocSession",
        "DriveSession",
        "FilesSession",
        "CalendarSession",
        "GmailSession",
    ],
)
def test_import_session_module(session_class):
    """Test that the session module can be imported."""
    import googau.sessions as session

    assert hasattr(session, session_class)  # nosec


@pytest.mark.parametrize("url", ["https://www.googleapis.com/auth/"])
def test_scopes_start_with_url(url):
    """Test that all scopes start with a pre-defined url."""
    import googau.sessions as session

    scopes_startswith = [scope.startswith(url) for scope in session.SCOPES]
    assert (len(set(scopes_startswith)) == 1) and (scopes_startswith[0] is True)


@patch("googau.sessions.GmailSession.__init__", return_value=None)
def test_gmail_session_init(mock_init):
    """Test GmailSession initialization."""
    session = GmailSession()
    assert session is not None
    mock_init.assert_called_once()


@patch("googau.sessions.SheetsSession.__init__", return_value=None)
def test_sheets_session_init(mock_init):
    """Test SheetsSession initialization."""
    session = SheetsSession()
    assert session is not None
    mock_init.assert_called_once()


@patch("googau.sessions.DocSession.__init__", return_value=None)
def test_doc_session_init(mock_init):
    """Test DocSession initialization."""
    session = DocSession()
    assert session is not None
    mock_init.assert_called_once()


@patch("googau.sessions.DriveSession.__init__", return_value=None)
def test_drive_session_init(mock_init):
    """Test DriveSession initialization."""
    session = DriveSession()
    assert session is not None
    mock_init.assert_called_once()


@patch("googau.sessions.FilesSession.__init__", return_value=None)
def test_files_session_init(mock_init):
    """Test FilesSession initialization."""
    session = FilesSession()
    assert session is not None
    mock_init.assert_called_once()


@patch("googau.sessions.CalendarSession.__init__", return_value=None)
def test_calendar_session_init(mock_init):
    """Test CalendarSession initialization."""
    session = CalendarSession()
    assert session is not None
    mock_init.assert_called_once()
