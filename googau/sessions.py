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
    "https://mail.google.com/",  # This scope has the permissions to delete emails
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
        token_path : str
            Path to token.pickle file.

        Returns
        -------
        Optional[Credentials]
            The authenticated credentials.

        """
        with open(token_path, "rb") as token:
            return pickle.load(token)  # nosec

    def authenticate(
        self, credentials: Optional[str] = None, token: Optional[str] = None
    ) -> Optional[Credentials]:
        """Authenticate user and return credentials.

        Parameters
        ----------
        credentials : Optional[str]
            Path to credentials.json file.
        token : Optional[str]
            Path to token.pickle file.

        Returns
        -------
        Optional[Credentials]
            The authenticated credentials.
            Returns None if credentials are not found or are invalid.

        """
        creds = None
        if token is not None and os.path.exists(token):
            creds = self._load_creds(token)
        elif token is None and os.path.exists(
            os.path.join(os.getcwd(), "token.pickle")
        ):
            creds = self._load_creds(os.path.join(os.getcwd(), "token.pickle"))

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:

            def _dump_creds(creds: Credentials) -> None:
                with open(
                    os.path.join(os.getcwd(), "token.pickle"), "wb"
                ) as token_file:
                    pickle.dump(creds, token_file)

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                _dump_creds(creds)
            elif credentials is not None:
                flow = InstalledAppFlow.from_client_secrets_file(credentials, SCOPES)
                new_creds: Credentials = flow.run_local_server(port=0)
                _dump_creds(new_creds)
            else:
                raise ValueError("No credentials found")
        return creds


class SheetsSession(GoogleSession):
    """GoogleSession for Sheets API."""

    def __init__(self, **kwargs):
        """Connect to Google Workspace Sheets API."""
        self.creds = self.authenticate(**kwargs)
        # pylint: disable=no-member
        self.session = build("sheets", "v4", credentials=self.creds).spreadsheets()


class DocSession(GoogleSession):
    """GoogleSession for Docs API."""

    def __init__(self, **kwargs):
        """Connect to Google Workspace Docs API."""
        self.creds = self.authenticate(**kwargs)
        # pylint: disable=no-member
        self.session = build("docs", "v1", credentials=self.creds).documents()


class DriveSession(GoogleSession):
    """GoogleSession for Drive API to manage shared drives."""

    def __init__(self, **kwargs):
        """Connect to Google Workspace Drive API."""
        self.creds = self.authenticate(**kwargs)
        # pylint: disable=no-member
        self.session = build("drive", "v3", credentials=self.creds).drives()

    def list_shared_drives(self):
        """List all shared drives."""
        response = self.session.list().execute()
        return response["drives"]


class FilesSession(GoogleSession):
    """GoogleSession for Drive API to manage files."""

    def __init__(self, **kwargs):
        """Connect to Google Workspace Drive API."""
        self.creds = self.authenticate(**kwargs)
        # pylint: disable=no-member
        self.session = build("drive", "v3", credentials=self.creds).files()


class CalendarSession(GoogleSession):
    """GoogleSession for Calendar API."""

    def __init__(self, **kwargs):
        """Connect to Google Workspace Calendar API."""
        self.creds = self.authenticate(**kwargs)
        # pylint: disable=no-member
        self.session = build("calendar", "v3", credentials=self.creds).events()


class GmailSession(GoogleSession):
    """GoogleSession for Gmail API."""

    def __init__(self, **kwargs):
        """Connect to Google Workspace Gmail API."""
        self.creds = self.authenticate(**kwargs)
        self.service = build("gmail", "v1", credentials=self.creds)

    def messages(self):
        """Get the Gmail messages."""
        return self.service.users().messages()
