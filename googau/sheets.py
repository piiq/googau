"""Spreadsheet utilities."""

from typing import List, Optional, Any, Union
from .sessions import SheetsSession
from .constants.sheets_constants import CONDITIONAL_FORMATTING_RULE


class WorkSheet(object):
    """Spreadsheet Worksheet object class.

    The worksheet is a page in the spreadsheet document. It contains the data.
    """

    sheetId: Optional[str] = None
    title: Optional[str] = None
    index: Optional[str] = None
    sheetType: Optional[str] = None
    gridProperties: Optional[str] = None
    hidden: Optional[str] = None
    tabColor: Optional[str] = None
    rightToLeft: Optional[bool] = False

    # pylint: disable=invalid-name
    def __init__(self, **kwargs):
        """Construct a worksheet instance."""
        self.sheetId = kwargs.get("sheetId", None)
        self.title = kwargs.get("title", None)
        self.index = kwargs.get("index", None)
        self.sheetType = kwargs.get("sheetType", None)
        self.gridProperties = kwargs.get("gridProperties", None)
        self.hidden = kwargs.get("hidden", None)
        self.tabColor = kwargs.get("tabColor", None)
        self.rightToLeft = kwargs.get("rightToLeft", False)

    def remove_key(self, d, key):
        """Remove key from dictionary utility function."""
        r = dict(d)
        del r[key]
        return r

    def to_json(self):
        """Return a json representation of the worksheet."""
        worksheet_json_object = {
            "sheetId": None,
            "title": None,
            "index": None,
            "sheetType": None,
            "gridProperties": None,
            "hidden": None,
            "tabColor": None,
            "rightToLeft": False,
        }
        for ws_key in self.__dict__:
            if vars(self)[ws_key] is not None:
                worksheet_json_object[ws_key] = vars(self)[ws_key]
            else:
                worksheet_json_object = self.remove_key(worksheet_json_object, ws_key)
        return worksheet_json_object

    def count_rows(self, sheet_session):
        """Count the number of rows in the worksheet.

        TODO: Implement this function
        """
        pass  # pylint: disable=unnecessary-pass

    def add_row(self):
        """Add a row to the worksheet.

        TODO: Implement this function
        """
        pass  # pylint: disable=unnecessary-pass

    def apply_cf_to_range(
        self,
        spreadsheet_id: str,
        sample_range: list,
        cf_style_dict: dict,
        sheet_session: SheetsSession,
    ) -> dict:
        """Apply conditional formatting to worksheet range.

        Parameters
        ----------
        spreadsheet_id : str
            The spreadsheet id from Google Sheets
        sample_range : list
            The range of cells to apply the conditional formatting
        cf_style_dict : dict
            A dictionary object containing the conditional formatting style
        sheet_session : SheetsSession
            A Google Sheets session object

        Returns
        -------
        dict
            A dictionary object containing the conditional formatting style

        """
        cfr = CONDITIONAL_FORMATTING_RULE
        for i in cf_style_dict:
            body: dict[str, Any] = {"requests": []}
            cfr["addConditionalFormatRule"]["rule"]["ranges"][0][
                "sheetId"
            ] = sample_range
            cfr["addConditionalFormatRule"]["rule"]["booleanRule"]["condition"][
                "values"
            ][0]["userEnteredValue"] = i
            cfr["addConditionalFormatRule"]["rule"]["booleanRule"]["format"][
                "backgroundColor"
            ]["blue"] = cf_style_dict[i]["blue"]
            cfr["addConditionalFormatRule"]["rule"]["booleanRule"]["format"][
                "backgroundColor"
            ]["green"] = cf_style_dict[i]["green"]
            cfr["addConditionalFormatRule"]["rule"]["booleanRule"]["format"][
                "backgroundColor"
            ]["red"] = cf_style_dict[i]["red"]
            body["requests"].append(cfr)
            result = sheet_session.session.batchUpdate(  # type: ignore
                spreadsheet_id=spreadsheet_id, body=body
            ).execute()
        return result


class SpreadSheet(object):
    """Gets a Spreadsheet object for the current session and an ID."""

    spreadsheet_id: Optional[str] = None
    session: SheetsSession

    def __init__(self, session: SheetsSession, spreadsheet_id: Optional[str] = None):
        """Construct an spreadsheet instance.

        Parameters
        ----------
        session : SheetsSession
            A Google Sheets session object
        spreadsheet_id : Optional[str], optional
            The spreadsheet id from Google Sheets, by default None

        """
        self.spreadsheet_id = spreadsheet_id
        self.session = session

    def new_worksheet(self, worksheet: WorkSheet):
        """Add new worksheet to spreadsheet.

        Parameters
        ----------
        worksheet : WorkSheet
            A dictionary object containing the worksheet properties

        Returns
        -------
        dict
            A dictionary object containing the worksheet properties

        """
        body = {"requests": [{"addSheet": {"properties": worksheet.to_json()}}]}
        result = self.session.batchUpdate(  # type: ignore
            spreadsheet_id=self.spreadsheet_id, body=body
        ).execute()
        return result

    def list_worksheets(self):
        """List available worksheets in the spreadsheet document.

        TODO: Implement this function

        Returns
        -------
        dict
            A dictionary object containing the available worksheets

        """

    def get_cell_range(self, cell_range: str) -> List[Union[str, int, float]]:
        """Get a range of cells from the spreadsheet.

        Parameters
        ----------
        cell_range : str
            The range of cells to get from the spreadsheet

        Returns
        -------
        List
            A list of strings or numbers containing the cell values

        """
        result = (
            self.session.session.values()
            .get(spreadsheetId=self.spreadsheet_id, range=cell_range)
            .execute()
        )
        values = result.get("values", [])
        return values

    def update_cell_range(
        self, cell_range: str, values: List, input_value_option: str = "RAW"
    ) -> dict:
        """Update a range of cells in the spreadsheet.

        Parameters
        ----------
        cell_range : str
            The range of cells to update in the spreadsheet
        values : List
            A list of strings or numbers containing the cell values
        input_value_option : str, optional
            The input value option, by default "RAW"

        Returns
        -------
        dict
            A dictionary object containing the updated cell values

        """
        body = {"values": values}
        result = (
            self.session.session.values()
            .update(
                spreadsheetId=self.spreadsheet_id,
                range=cell_range,
                valueInputOption=input_value_option,
                body=body,
            )
            .execute()
        )
        print(f"Updated {result.get('updatedCells')} cells.")
        return result

    # except HttpError as error:
    #     print(f"An error occurred: {error}")
    #     return error
