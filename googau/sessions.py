"""Google Workspace API session management helpers."""

import os
import pickle  # nosec
from typing import Optional
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# If modifying these scopes, delete the token.pickle file.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]


class GoogleSession:
    """Base class that helps authenticate and authorize user.

    This class is parent to all application specific auth classes.
    """

    creds: Optional[Credentials] = None

    def _load_creds(self, token_path: str) -> Optional[Credentials]:
        """Load credentials from token.pickle.

        Parameters
        ----------
            token_path (str): Path to token.pickle file.

        Returns
        -------
            Optional[Credentials]: Credentials.
        """
        with open(token_path, "rb") as token:
            return pickle.load(token)  # nosec

    def authenticate(self, credentials_json: str = "credentials.json") -> str:
        """Authenticate user and return credentials.

        Parameters
        ----------
            credentials_json (str, optional): Path to credentials.json file.
            Defaults to "credentials.json".

        Returns
        -------
            str: Credentials.
        """
        creds = None
        if os.path.exists("token.pickle"):
            self._load_creds("token.pickle")
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_json, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return creds


class SheetsSession(GoogleSession):
    """GoogleSession for Sheets API."""

    def __init__(self, credentials_json="credentials.json"):
        """Connect to Google Workspace Sheets API."""
        self.creds = self.authenticate(credentials_json=credentials_json)
        # pylint: disable=no-member
        self.session = build("sheets", "v4", credentials=self.creds).spreadsheets()


class DocSession(GoogleSession):
    """GoogleSession for Docs API."""

    def __init__(self, credentials_json="credentials.json"):
        """Connect to Google Workspace Docs API."""
        self.creds = self.authenticate(credentials_json=credentials_json)
        # pylint: disable=no-member
        self.session = build("docs", "v1", credentials=self.creds).documents()


class DriveSession(GoogleSession):
    """GoogleSession for Drive API to manage shared drives."""

    def __init__(self, credentials_json="credentials.json"):
        """Connect to Google Workspace Drive API."""
        self.creds = self.authenticate(credentials_json=credentials_json)
        # pylint: disable=no-member
        self.session = build("drive", "v3", credentials=self.creds).drives()

    def list_shared_drives(self):
        """List all shared drives."""
        response = self.session.list().execute()
        return response["drives"]


class FilesSession(GoogleSession):
    """GoogleSession for Drive API to manage files."""

    def __init__(self, credentials_json="credentials.json"):
        """Connect to Google Workspace Drive API."""
        self.creds = self.authenticate(credentials_json=credentials_json)
        # pylint: disable=no-member
        self.session = build("drive", "v3", credentials=self.creds).files()


class CalendarSession(GoogleSession):
    """GoogleSession for Calendar API."""

    def __init__(self, credentials_json="credentials.json"):
        """Connect to Google Workspace Calendar API."""
        self.creds = self.authenticate(credentials_json)
        # pylint: disable=no-member
        self.session = build("calendar", "v3", credentials=self.creds).events()
