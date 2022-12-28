"""Constants and object templates for the Google Sheets API."""

CONDITIONAL_FORMATTING_RULE: dict = {
    "addConditionalFormatRule": {
        "rule": {
            "ranges": [
                {
                    "endColumnIndex": 2,
                    "sheetId": None,
                    "startColumnIndex": 0,
                    "startRowIndex": 3,
                }
            ],
            "booleanRule": {
                "condition": {
                    "type": "TEXT_EQ",
                    "values": [{"userEnteredValue": None}],
                },
                "format": {
                    "backgroundColor": {"blue": None, "green": None, "red": None},
                    "textFormat": {
                        "foregroundColor": {"red": 1, "green": 1, "blue": 1, "alpha": 1}
                    },
                },
            },
        }
    }
}
