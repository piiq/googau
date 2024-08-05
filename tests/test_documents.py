import pytest
from unittest.mock import patch
from googau.documents import Doc
from googau.sessions import DocSession


@pytest.fixture
@patch("googau.sessions.DocSession.__init__", return_value=None)
def doc_session(mock_init):
    session = DocSession()
    return session


def test_doc_init(doc_session):
    document = Doc(session=doc_session, documentId="test_document_id")
    assert document is not None
    assert document.documentId == "test_document_id"
    assert document.session == doc_session
