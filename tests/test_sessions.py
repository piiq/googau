"""Test the sessions module."""

import pytest

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
    ],
)
def test_import_session_module(session_class):
    """Test that the session module can be imported."""
    import googau.sessions as session

    assert hasattr(session, session_class)  # nosec


@pytest.mark.parametrize("url", ["https://www.googleapis.com/auth/"])
def test_scopes_start_with_url(url):
    """Test that all scopes start with a pre-defined url."""
    # Import the session module from the googau package
    import googau.sessions as session

    url = "https://www.googleapis.com/auth/"

    scopes_startswith = [scope.startswith(url) for scope in session.SCOPES]
    assert (len(set(scopes_startswith)) == 1) and (  # nosec
        scopes_startswith[0] is True
    )
