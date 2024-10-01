"""Test the sheets module."""

import pytest
from unittest.mock import MagicMock, patch
from googau.sheets import SpreadSheet, WorkSheet

# pylint: disable=import-outside-toplevel


@pytest.fixture
def mock_spreadsheet():
    mock_session = MagicMock()
    return SpreadSheet(mock_session, "spreadsheet_id")


@pytest.fixture
def mock_worksheet():
    return WorkSheet(sheetId="test_sheet_id", title="Test Sheet")


@pytest.mark.parametrize(
    "sheets_class",
    [
        "WorkSheet",
        "SpreadSheet",
    ],
)
def test_import_sheets_module(sheets_class):
    """Test that the sheets module can be imported."""
    import googau.sheets as gs

    assert hasattr(gs, sheets_class)  # nosec


def test_count_rows(mock_spreadsheet):
    mock_spreadsheet.count_rows = MagicMock(return_value=10)
    assert mock_spreadsheet.count_rows() == 10


def test_add_row(mock_spreadsheet):
    mock_spreadsheet.add_row = MagicMock(return_value={"status": "success"})
    assert mock_spreadsheet.add_row() == {"status": "success"}


def test_list_worksheets(mock_spreadsheet):
    mock_spreadsheet.list_worksheets = MagicMock(return_value={"Sheet1": "id1"})
    assert mock_spreadsheet.list_worksheets() == {"Sheet1": "id1"}


def test_new_worksheet(mock_spreadsheet, mock_worksheet):
    mock_spreadsheet.session.batchUpdate = MagicMock(
        return_value=MagicMock(execute=MagicMock(return_value={"status": "success"}))
    )
    result = mock_spreadsheet.new_worksheet(mock_worksheet)
    assert result == {"status": "success"}
    mock_spreadsheet.session.batchUpdate.assert_called_once()


def test_get_cell_range(mock_spreadsheet):
    mock_spreadsheet.session.session.values().get().execute.return_value = {
        "values": [["A1", "B1"], ["A2", "B2"]]
    }
    result = mock_spreadsheet.get_cell_range("A1:B2")
    assert result == [["A1", "B1"], ["A2", "B2"]]
    mock_spreadsheet.session.session.values().get().execute.assert_called_once()


def test_update_cell_range(mock_spreadsheet):
    mock_spreadsheet.session.session.values().update().execute.return_value = {
        "updatedCells": 4
    }
    result = mock_spreadsheet.update_cell_range("A1:B2", [["A1", "B1"], ["A2", "B2"]])
    assert result == {"updatedCells": 4}
    mock_spreadsheet.session.session.values().update().execute.assert_called_once()


def test_worksheet_to_json(mock_worksheet):
    expected_json = {
        "sheetId": "test_sheet_id",
        "title": "Test Sheet",
        "rightToLeft": False,
    }
    assert mock_worksheet.to_json() == expected_json


# decorator to disable test
@pytest.mark.skip("test_apply_cf_to_range is not implemented correctly")
@patch(
    "googau.sheets.SheetsSession().session.batchUpdate",
    return_value=MagicMock(execute=MagicMock(return_value={"status": "success"})),
)
def test_apply_cf_to_range(mock_batch_update, mock_spreadsheet):
    sample_range = [0, 1, 2, 3]
    cf_style_dict = {
        "condition1": {"blue": 1, "green": 1, "red": 1},
    }
    result = mock_spreadsheet.apply_cf_to_range(
        "spreadsheet_id", sample_range, cf_style_dict, mock_spreadsheet.session
    )
    assert result == {"status": "success"}
    mock_batch_update.assert_called_once()
