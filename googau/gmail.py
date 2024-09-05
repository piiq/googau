import base64
import random
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from googleapiclient.errors import HttpError

from .sessions import GmailSession


class GmailEmail(object):
    """Gmail Email object class.

    The email is the message itself.
    It contains headers and body that can be encoded in different ways.

    This wrapper class exposes some of the headers and body that make it easier to
    process and use.
    """

    date: datetime
    sent_from: str
    sent_to: str
    labels: Optional[list]
    cc: Optional[str]
    subject: Optional[str]
    text_content: Optional[str]

    _raw_message: Optional[dict]

    def __init__(self, date: datetime, sent_from: str, sent_to: str, **kwargs) -> None:
        self.date = date
        self.sent_from = sent_from
        self.sent_to = sent_to

        self.cc = kwargs.get("cc", None)
        self.subject = kwargs.get("cc", None)
        self.text_content = kwargs.get("text_content", None)

        self._raw_message = kwargs.get("raw_message", None)

    @classmethod
    def _filter_header(cls, message: dict, header_name: str) -> Optional[str]:
        return next(
            (
                header["value"]
                for header in message["payload"]["headers"]
                if header["name"] == header_name
            ),
            None,
        )

    @classmethod
    def _get_text_content(cls, message: dict) -> Optional[str]:
        def extract_text(parts):
            text_content = ""
            for part in parts:
                if part["mimeType"] == "text/plain":
                    encoded_string = part["body"]["data"]
                    decoded_string = base64.urlsafe_b64decode(encoded_string).decode(
                        "utf-8"
                    )
                    text_content += decoded_string
                elif part["mimeType"].startswith("multipart/"):
                    text_content += extract_text(part.get("parts", []))
            return text_content

        payload = message.get("payload", {})
        if payload.get("mimeType") == "multipart/mixed":
            for part in payload.get("parts", []):
                if part.get("mimeType") == "multipart/related":
                    for subpart in part.get("parts", []):
                        if subpart.get("mimeType") == "multipart/alternative":
                            return extract_text(subpart.get("parts", []))
        return extract_text(payload.get("parts", []))

    @classmethod
    def from_raw_message(cls, message: dict) -> "GmailEmail":
        raw_date = cls._filter_header(message, "Date")
        sent_from = cls._filter_header(message, "From")
        sent_to = cls._filter_header(message, "To")
        for h in [raw_date, sent_from, sent_to]:
            if h is None:
                raise ValueError(f"{h} header not found in message")

        subject = cls._filter_header(message, "Subject")
        cc = cls._filter_header(message, "Cc")
        text_content = cls._get_text_content(message)

        # Handle 'GMT' in date string
        if "GMT" in raw_date:
            raw_date = raw_date.replace("GMT", "+0000")

        # Remove extra timezone information specified in parentheses
        if "(" in raw_date:
            raw_date = raw_date.split(" (")[0]

        date = datetime.strptime(raw_date, "%a, %d %b %Y %H:%M:%S %z")
        # Convert the local datetime to UTC timezone (but keep it naive)
        utc_converted_datetime = date.replace(tzinfo=None)

        return cls(
            date=utc_converted_datetime,
            sent_from=sent_from,
            sent_to=sent_to,
            cc=cc,
            subject=subject,
            text_content=text_content,
            raw_message=message,
        )

    def to_json(self, exclude_raw: bool = False) -> dict:
        """Convert the GmailEmail object to a JSON-serializable dictionary."""
        message_dict = {
            "date": self.date.isoformat(),
            "sent_from": self.sent_from,
            "sent_to": self.sent_to,
            "cc": self.cc,
            "subject": self.subject,
            "text_content": self.text_content,
            "raw_message": self._raw_message,
        }
        if exclude_raw:
            message_dict.pop("raw_message", None)

        return message_dict

    def __repr__(self) -> str:
        repr_string = "GmailEmail:\n"
        repr_string += f"date={self.date.isoformat()}\n"
        repr_string += f"sent_from={self.sent_from}\n"
        repr_string += f"sent_to={self.sent_to}\n"
        repr_string += f"cc={self.cc}\n"
        repr_string += f"subject={self.subject}\n"
        repr_string += f"text_content={self.text_content}\n"
        return repr_string


class GmailMailbox(object):
    """GmailMailbox object for the current session."""

    def __init__(self, session: GmailSession):
        self.session = session

    def get_message(self, user_id: str = "me", msg_id: str = "") -> Dict:
        """Get a single specific message by ID.

        Parameters
        ----------
        user_id : str, optional
            The user ID for the search, by default "me" (the currently authenticated user)
        msg_id : str, optional
            The message ID to retrieve, by default ""
        """
        message = self.session.messages().get(userId=user_id, id=msg_id).execute()
        return message

    def get_messages(self, user_id: str = "me", msg_ids: List[str] = []) -> List[Dict]:
        """Get a list of specific messages by their IDs using batch requests.

        Gmail API has a strict rate limit that allows retrieving about 50 emails per second.
        Given that search of a mailbox will likely return more than 50 emails, we need to
        make multiple batch requests to retrieve all the emails.

        The maximum number of requests in a batch request shall not exceed 100.

        Parameters
        ----------
        user_id : str, optional
            The user ID for the search, by default "me"
        msg_ids : List[str], optional
            The list of message IDs to retrieve, by default []
        """
        messages = []
        failed_ids = msg_ids.copy()
        request_id_to_msg_id = {}
        max_retries = 5

        for attempt in range(max_retries):
            if not failed_ids:
                break

            # Split the list of messages that need to be retrieved into chunks of 100
            chunks = [failed_ids[i : i + 100] for i in range(0, len(failed_ids), 100)]

            for chunk in chunks:
                batch = self.session.service.new_batch_http_request(
                    callback=self._batch_callback(
                        messages, request_id_to_msg_id, failed_ids
                    )
                )

                for msg_id in chunk:
                    request = self.session.messages().get(userId=user_id, id=msg_id)
                    request_id = str(uuid.uuid4())
                    batch.add(request, request_id=request_id)
                    request_id_to_msg_id[request_id] = msg_id

                self._execute_batch_with_retries(batch)

            if not failed_ids:
                break

            wait_time = (2**attempt) + (random.randint(0, 1000) / 1000)
            time.sleep(wait_time)

        return messages

    def _batch_callback(self, messages, request_id_to_msg_id, failed_ids):
        def callback(request_id, response, exception):
            msg_id = request_id_to_msg_id.get(request_id)
            if msg_id:
                if exception is None:
                    messages.append(response)
                    failed_ids.remove(msg_id)

        return callback

    def _execute_batch_with_retries(self, batch, max_retries=5):
        """Execute the batch request with retries on rate limit errors."""
        for attempt in range(max_retries):
            try:
                batch.execute()
                break
            except HttpError as error:
                if error.resp.status == 429:
                    wait_time = (2**attempt) + (random.randint(0, 1000) / 1000)
                    time.sleep(wait_time)
                else:
                    raise

    def search_messages(
        self,
        user_id: str = "me",
        query: str = "",
        after: Optional[str] = None,
        before: Optional[str] = None,
        limit: Optional[int] = None,
        label_ids: Optional[List[str]] = None,
        search_spam: bool = False,
        search_trash: bool = False,
    ) -> List[Dict]:
        """Search for messages in the user's mailbox based on query and date range.

        Parameters
        ----------
        user_id : str, optional
            The user ID for the search, by default "me" (the currently authenticated user)
        query : str, optional
            The query for the search, by default ""
        after : Optional[str], optional
            The start date for the search, by default None
        before : Optional[str], optional
            The end date for the search, by default None
        limit : Optional[int], optional
            The maximum number of messages to return, by default None.
            Google defaults to 100 and maxes out at 500.
        label_ids : Optional[List[str]], optional
            The label IDs for the search, by default None
        search_spam : bool, optional
            Whether to search the spam folder, by default False
        search_trash : bool, optional
            Whether to search the trash folder, by default False
        """
        if after:
            query += f" after:{after}"
        if before:
            query += f" before:{before}"
        if label_ids:
            query += f" labelIds:{','.join(label_ids)}"
        if search_spam:
            query += " in:spam"
        if search_trash:
            query += " in:trash"

        messages = []
        page_token = None
        fetched_count = 0
        max_per_request = 500  # Gmail API max limit per request

        while True:
            current_limit = (
                min(max_per_request, limit - fetched_count)
                if limit
                else max_per_request
            )
            response = (
                self.session.messages()
                .list(
                    userId=user_id,
                    q=query,
                    maxResults=current_limit,
                    pageToken=page_token,
                )
                .execute()
            )
            messages.extend(response.get("messages", []))
            fetched_count += len(response.get("messages", []))
            page_token = response.get("nextPageToken")
            if not page_token or (limit and fetched_count >= limit):
                break

        return messages[:limit] if limit else messages
