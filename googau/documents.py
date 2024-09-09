"""Document utilities."""

from typing import Optional
from .sessions import DocSession


class Doc(object):
    """Gets a Document object for the current session and an ID."""

    documentId: Optional[str] = None
    session: Optional[DocSession] = None

    # pylint: disable=invalid-name
    def __init__(self, session=None, documentId=None):
        """Construct a document instance.

        Parameters
        ----------
        session : Optional[DocSession], optional
            The Google Docs API session to use, by default None
        documentId : Optional[str], optional
            The document id from Google Docs, by default None

        """
        self.documentId = documentId
        self.session = session
