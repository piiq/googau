import pytest
from unittest.mock import patch, MagicMock
from googau.gmail import GmailSession, GmailMailbox


@pytest.fixture
@patch("googau.gmail.GmailSession.__init__", return_value=None)
def gmail_mailbox(mock_init):
    session = GmailSession()
    mailbox = GmailMailbox(session)
    mailbox.search_messages = MagicMock(return_value=[])
    mailbox.get_messages = MagicMock(return_value={})
    return mailbox


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "query": "github",
            "after": "2024/07/01",
            "before": "2024/07/31",
        },
        {
            "query": "python",
            "after": "2024/06/01",
            "before": "2024/06/30",
            "search_spam": True,
        },
        {
            "query": "pytest",
            "after": "2024/05/01",
            "before": "2024/05/31",
            "search_trash": True,
        },
    ],
)
def test_search_messages_mailbox(gmail_mailbox, kwargs):
    messages = gmail_mailbox.search_messages(**kwargs)
    assert isinstance(messages, list)


def test_get_messages_mailbox(gmail_mailbox):
    message_ids = ["sample_message_id"]
    messages = gmail_mailbox.get_messages(msg_ids=message_ids)
    assert isinstance(messages, dict)
