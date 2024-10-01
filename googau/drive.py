"""Google Drive API wrapper."""

from typing import Optional
import copy
from .sessions import DriveSession
from .constants.drive_constants import SHARED_DRIVE


class SharedDrive(object):
    """SharedDrive object for the current session and an ID."""

    drive_id: Optional[str] = None
    session: DriveSession

    def __init__(self, session: DriveSession, drive_id: Optional[str] = None):
        """Construct an shared drive instance.

        Parameters
        ----------
        session : DriveSession
            A DriveSession instance
        drive_id : Optional[str], optional
            The shared drive id from G-Suite, by default None

        """
        self.drive_id = drive_id
        self.session = session

    def get_drive_contents(self, drive_id: Optional[str]):
        """Get the contents of a shared drive.

        TODO: Implement this method.
        """
        drive_id = drive_id or self.drive_id

    def create(self, request_id: str, name: str, **kwargs) -> dict:
        """Create a shared drive.

        Parameters
        ----------
        request_id : str
            A unique request ID (UUID4)
        name : str
            The name of the shared drive
        **kwargs : dict
            Additional arguments to pass to the API call.

        Returns
        -------
        dict
            The response from the API call.

        """
        drive_template = copy.deepcopy(SHARED_DRIVE)
        drive_template["name"] = name
        if "orgUnitId" in kwargs:
            drive_template["orgUnitId"] = kwargs["orgUnitId"]

        response = self.session.session.create(
            requestId=request_id, body=drive_template
        ).execute()

        return response

    def hide(self) -> dict:
        """Hide a shared drive.

        Returns
        -------
        dict
            The response from the API call.

        """
        if self.drive_id is None:
            return {"error": "No Drive ID provided."}
        response = self.session.session.hide(driveId=self.drive_id).execute()
        return response

    def unhide(self) -> dict:
        """Unhide a shared drive.

        Returns
        -------
        dict
            The response from the API call.

        """
        if self.drive_id is None:
            return {"error": "No Drive ID provided."}
        response = self.session.session.unhide(driveId=self.drive_id).execute()
        return response
