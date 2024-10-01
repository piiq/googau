import pytest
from unittest.mock import patch
from googau.drive import SharedDrive
from googau.sessions import DriveSession


@pytest.fixture
@patch("googau.sessions.DriveSession.__init__", return_value=None)
def drive_session(mock_init):
    session = DriveSession()
    return session


def test_drive_init(drive_session):
    drive = SharedDrive(session=drive_session, drive_id="test_drive_id")
    assert drive is not None
    assert drive.drive_id == "test_drive_id"


@patch("googau.drive.SharedDrive.create", return_value={})
def test_create_drive(mock_create, drive_session):
    drive = SharedDrive(session=drive_session, drive_id="test_drive_id")
    result = drive.create(request_id="test_request_id", name="test_drive")
    assert isinstance(result, dict)
    mock_create.assert_called_once()
